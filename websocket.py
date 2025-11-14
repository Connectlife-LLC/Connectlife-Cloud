"""WebSocket client for ConnectLife Cloud."""

from __future__ import annotations

import asyncio
import base64
import binascii
import json
import logging
import time
import uuid
from typing import Any, Awaitable, Callable, Optional

import aiohttp

from .client import ConnectLifeCloudClient
from .models import NotificationInfo

LOGGER = logging.getLogger(__name__)

MessageCallback = Callable[[dict[str, Any]], None]
TokenGetter = Callable[[], Awaitable[str]]


class ConnectLifeWebSocket:
    """WebSocket client that streams real-time device updates."""

    def __init__(
        self,
        client: ConnectLifeCloudClient,
        session: aiohttp.ClientSession,
        token_getter: TokenGetter,
        message_callback: MessageCallback,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        self._client = client
        self._session = session
        self._get_token = token_getter
        self._message_callback = message_callback
        self._loop = loop or asyncio.get_event_loop()
        self._ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self._task: Optional[asyncio.Task] = None
        self._phone_code: str = ""
        self._notification_info: Optional[NotificationInfo] = None
        self._closing = False
        self._fail_count = 0
        self._max_fails = 3
        self._ping_interval = 30
        self._last_message_time = 0.0

    async def _generate_phone_code(self) -> str:
        phone_code = str(uuid.uuid4())
        LOGGER.debug("Generated phone code: %s", phone_code)
        return phone_code

    async def _register_phone_code(self, access_token: str) -> bool:
        if not self._phone_code:
            return False
        return await self._client.register_phone_device(self._phone_code, access_token)

    async def _load_notification_info(self, access_token: str) -> None:
        if not self._phone_code:
            return
        self._notification_info = await self._client.get_notification_info(
            self._phone_code, access_token
        )
        if self._notification_info:
            self._ping_interval = self._notification_info.hb_interval
            self._max_fails = self._notification_info.hb_fail_times

    async def _connect_ws(self) -> None:
        if not self._notification_info or not self._phone_code:
            LOGGER.error("Missing notification info or phone code")
            return

        channel = (
            self._notification_info.push_channels[0].push_channel
            if self._notification_info.push_channels
            else ""
        )
        if not channel:
            LOGGER.error("No push channel available")
            return

        try:
            access_token = await self._get_token()
            ws_url = (
                f"wss://{self._notification_info.push_server_ip}:"
                f"{self._notification_info.push_server_ssl_port}/ws/{channel}"
                f"?phoneCode={self._phone_code}&token={access_token}"
            )
            LOGGER.debug("Connecting to WebSocket URL: %s", ws_url)

            self._ws = await self._session.ws_connect(
                ws_url, heartbeat=self._ping_interval, ssl=True
            )
            LOGGER.info("WebSocket connection established")
            self._fail_count = 0
            await self._listen()
        except aiohttp.ClientError as err:
            LOGGER.error("WebSocket connection failed: %s", err)
            await self._schedule_reconnect()

    async def _listen(self) -> None:
        if not self._ws:
            return
        try:
            async for msg in self._ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    now = time.time()
                    if now - self._last_message_time < 1:
                        continue
                    self._last_message_time = now
                    await self._handle_message(msg.data)
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    LOGGER.error("WebSocket error: %s", self._ws.exception())
                    break
                elif msg.type == aiohttp.WSMsgType.CLOSED:
                    LOGGER.debug("WebSocket closed by server")
                    break
        except Exception as err:
            LOGGER.error("WebSocket listener error: %s", err)
        finally:
            if not self._closing:
                await self._schedule_reconnect()

    async def _handle_message(self, raw_message: str) -> None:
        try:
            base64_decoded = base64.b64decode(raw_message)
            decoded_content = base64_decoded.decode("utf-8")
            data = json.loads(decoded_content)
            self._message_callback(data)
        except (binascii.Error, UnicodeDecodeError, json.JSONDecodeError) as err:
            LOGGER.error("Failed to decode WebSocket message: %s", err)

    async def _schedule_reconnect(self) -> None:
        self._fail_count += 1
        if self._fail_count > self._max_fails:
            LOGGER.error("Maximum WebSocket retries reached")
            return

        delay = min(30, 5 * (2 ** (self._fail_count - 1)))
        LOGGER.debug("Reconnecting WebSocket in %s seconds", delay)
        await asyncio.sleep(delay)

        if self._closing:
            return

        access_token = await self._get_token()
        await self._load_notification_info(access_token)
        if self._notification_info:
            self._task = self._loop.create_task(self._connect_ws())

    async def async_connect(self) -> None:
        """Initialize and connect the WebSocket."""
        try:
            self._closing = False
            self._phone_code = await self._generate_phone_code()

            access_token = await self._get_token()
            if not await self._register_phone_code(access_token):
                LOGGER.error("Failed to register phone code")
                return

            await self._load_notification_info(access_token)
            if not self._notification_info:
                LOGGER.error("Failed to load notification data")
                return

            self._task = self._loop.create_task(self._connect_ws())
        except Exception as err:
            LOGGER.error("Failed to connect WebSocket: %s", err)

    async def async_disconnect(self) -> None:
        """Disconnect from the WebSocket."""
        self._closing = True
        if self._ws:
            await self._ws.close()
            self._ws = None
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        LOGGER.debug("WebSocket disconnected")

