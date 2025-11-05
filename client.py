"""ConnectLife Cloud API client."""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import logging
import re
import time
import uuid
from base64 import b64encode
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

import aiohttp
import pytz

from .device_manager import DeviceParserFactory
from .devices import get_device_parser
from .devices.atw_035_699 import SplitWater035699Parser
from .devices.base import BaseDeviceParser
from .devices.base_bean import BaseBeanParser
from .devices.bean_006_299 import Split006299Parser
from .devices.hum_007 import Humidity007Parser
from .exceptions import (
    ConnectLifeCloudAPIError,
    ConnectLifeCloudAuthError,
    ConnectLifeCloudConnectionError,
    ConnectLifeCloudError,
)
from .models import DeviceInfo, DeviceStatus

_LOGGER = logging.getLogger(__name__)


class ConnectLifeCloudClient:
    """ConnectLife Cloud API client."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        base_url: str = "https://juapi-3rd.hijuconn.com",
        oauth_url: str = "https://oauth.hijuconn.com",
        session: Optional[aiohttp.ClientSession] = None,
    ) -> None:
        """Initialize the client."""
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url.rstrip("/")
        self.oauth_url = oauth_url.rstrip("/")
        self.session = session or aiohttp.ClientSession()
        self._source_id: Optional[str] = None
        self._devices: Dict[str, DeviceInfo] = {}
        self._parsers: Dict[str, BaseDeviceParser] = {}
        self._static_data: Dict[str, Any] = {}
        self._status_callbacks: Dict[str, Callable[[Dict[str, Any]], None]] = {}

    async def close(self) -> None:
        """Close the client session."""
        if self.session and not self.session.closed:
            await self.session.close()

    def _generate_uuid(self) -> str:
        """Generate a UUID string without dashes."""
        return f"{uuid.uuid1().hex}{int(time.time() * 1000)}"

    def _get_source_id(self) -> str:
        """Get or generate source ID."""
        if not self._source_id:
            uuid_str = self._generate_uuid()
            md5_uuid = hashlib.md5(uuid_str.encode()).hexdigest()
            self._source_id = f"td001002000{md5_uuid}"
        return self._source_id

    def _calculate_signature_sha256(self, secret: str, params: str) -> str:
        """Calculate HMAC-SHA256 signature."""
        return b64encode(
            hmac.new(
                bytes(secret, "utf-8"), bytes(params, "utf-8"), hashlib.sha256
            ).digest()
        ).decode("utf-8")

    def _calculate_body_digest_sha256(self, body: Optional[Dict[str, Any]]) -> str:
        """Calculate SHA-256 digest of request body."""
        if body and len(body) > 0:
            return b64encode(
                hashlib.sha256(json.dumps(body).encode("utf-8")).digest()
            ).decode("utf-8")
        return "47DEQpj8HBSa+/TImW+5JCeuQeRkm5NMpJWZG3hSuFU="

    def _calculate_gmt_date(self) -> str:
        """Calculate GMT date string."""
        gmt_format = "%a, %d %b %Y %H:%M:%S GMT"
        return datetime.now(pytz.utc).strftime(gmt_format)

    def _calculate_path(self, url: str) -> str:
        """Extract path from URL."""
        return re.sub(r"^https://[^/]*", "", url)

    def _calculate_encrypt(
        self, secret_key: str, method: str, path: str, gmt_date: str, header: str
    ) -> str:
        """Calculate encryption string for signature."""
        return f"{secret_key}\n{method} {path}\ndate: {gmt_date}\n{header}\n"

    async def _get_system_parameters(self, access_token: Optional[str] = None) -> Dict[str, Any]:
        """Generate system parameters."""
        timestamp = int(time.time() * 1000)
        uuid_str = str(uuid.uuid1()) + str(timestamp)
        random_str = hashlib.md5(uuid_str.encode()).hexdigest()

        params = {
            "timeStamp": str(timestamp),
            "version": "8.1",
            "languageId": "1",
            "timezone": "UTC",
            "randStr": random_str,
            "appId": self.client_id,
            "sourceId": self._get_source_id(),
            "platformId": 5,
        }

        if access_token:
            params["accessToken"] = access_token

        return params

    async def _api_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        access_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Make an API request."""
        _LOGGER.debug("Making API request: %s %s", method, endpoint)

        try:
            # Get system parameters
            params = await self._get_system_parameters(access_token)

            # Merge with provided data if any
            request_data = data if data else {}
            request_data.update(params)

            if headers is None:
                headers = {}

            # Add accessToken to headers only for GET requests
            if method.upper() == "GET" and access_token:
                headers["accessToken"] = access_token

            # Build full URL
            url = f"{self.base_url}{endpoint}"

            # For GET requests, append parameters to URL
            if method.upper() == "GET":
                query_params = []
                url_params = request_data.copy()
                url_params.pop("accessToken", None)

                for key, value in url_params.items():
                    if isinstance(value, (dict, list)):
                        value = json.dumps(value)
                    query_params.append(f"{key}={value}")
                query_string = "&".join(query_params)
                url = f"{url}?{query_string}"
                request_data = None

            # Calculate signature
            gmt_date = self._calculate_gmt_date()
            header_key = "hi-params-encrypt"
            encrypt_params = self._calculate_encrypt(
                self.client_id,
                method,
                self._calculate_path(url),
                gmt_date,
                f"{header_key}: {self.client_id}",
            )

            sign = self._calculate_signature_sha256(self.client_secret, encrypt_params)

            # Prepare headers
            headers.update({
                header_key: self.client_id,
                "Date": gmt_date,
                "Authorization": f'Signature signature="{sign}", keyId="{self.client_id}",algorithm="hmac-sha256", headers="@request-target date {header_key}"',
                "Content-Type": "application/json",
                "Digest": f"SHA-256={self._calculate_body_digest_sha256(request_data)}",
            })

            # Convert request_data to JSON string for POST requests
            json_data = json.dumps(request_data) if request_data else None

            async with self.session.request(
                method, url, data=json_data, headers=headers
            ) as resp:
                response_text = await resp.text()

                _LOGGER.debug("Response status: %d", resp.status)
                _LOGGER.debug("Response body: %s", response_text)

                resp.raise_for_status()

                try:
                    response_data = json.loads(response_text)
                except json.JSONDecodeError as err:
                    raise ConnectLifeCloudAPIError(f"Invalid JSON response: {response_text}")

                if not isinstance(response_data, dict):
                    raise ConnectLifeCloudAPIError(f"Unexpected response format: {response_data}")

                if response_data.get("resultCode") != 0:
                    error_msg = response_data.get("msg", "Unknown error")
                    raise ConnectLifeCloudAPIError(f"API error: {error_msg}")

                return response_data

        except aiohttp.ClientError as err:
            raise ConnectLifeCloudConnectionError(f"HTTP request failed: {err}")
        except Exception as err:
            raise ConnectLifeCloudError(f"API request failed: {err}")

    async def get_devices(self, access_token: str) -> Dict[str, DeviceInfo]:
        """Get list of devices with their current status."""
        _LOGGER.debug("Fetching device list with status")

        try:
            response = await self._api_request(
                "GET", "/clife-svc/pu/get_device_status_list", access_token=access_token
            )

            if not response:
                return {}

            devices = {}
            device_list = response.get("deviceList", [])
            _LOGGER.debug("Found %d devices in response", len(device_list))

            for device_data in device_list:
                device_type_code = device_data.get("deviceTypeCode")
                if device_type_code in ["009", "008", "007", "006", "016", "035"]:
                    device = DeviceInfo.from_api_data(device_data)
                    devices[device.device_id] = device
                    self._devices[device.device_id] = device
                    _LOGGER.debug("Added device: %s", device.debug_info())

            return devices

        except Exception as err:
            _LOGGER.error("Failed to fetch devices: %s", err)
            raise ConnectLifeCloudError(f"Error communicating with API: {err}")

    async def control_device(
        self, puid: str, properties: Dict[str, Any], access_token: str
    ) -> Dict[str, Any]:
        """Control device by setting properties."""
        _LOGGER.debug("Controlling device %s with properties: %s", puid, properties)

        try:
            params = {
                "puid": puid,
                "properties": properties,
            }

            response = await self._api_request(
                "POST", "/device/pu/property/set", data=params, access_token=access_token
            )

            if response.get("resultCode") == 0:
                return {
                    "success": True,
                    "status": response.get("kvMap", {}),
                }
            else:
                error_msg = response.get("msg", "Unknown error")
                raise ConnectLifeCloudAPIError(f"Control failed: {error_msg}")

        except Exception as err:
            raise ConnectLifeCloudError(f"Failed to control device: {err}")

    async def get_property_list(
        self, device_type_code: str, device_feature_code: str, access_token: str
    ) -> Dict[str, Any]:
        """Get device property list."""
        try:
            params = {
                "deviceTypeCode": device_type_code,
                "deviceFeatureCode": device_feature_code,
            }

            response = await self._api_request(
                "GET", "/clife-svc/get_property_list", data=params, access_token=access_token
            )

            if response.get("resultCode") == 0:
                return {
                    "success": True,
                    "status": response.get("properties", {}),
                }
            else:
                error_msg = response.get("msg", "Unknown error")
                raise ConnectLifeCloudAPIError(f"Failed to get property list: {error_msg}")

        except Exception as err:
            raise ConnectLifeCloudError(f"Failed to get property list: {err}")

    async def query_static_data(self, puid: str, access_token: str) -> Dict[str, Any]:
        """Query static data for device."""
        try:
            params = {"puid": puid}

            response = await self._api_request(
                "POST", "/clife-svc/pu/query_static_data", data=params, access_token=access_token
            )

            if response.get("resultCode") == 0:
                return {
                    "success": True,
                    "status": response.get("data"),
                }
            else:
                error_msg = response.get("msg", "Unknown error")
                raise ConnectLifeCloudAPIError(f"Failed to query static data: {error_msg}")

        except Exception as err:
            raise ConnectLifeCloudError(f"Failed to query static data: {err}")

    async def get_hour_power(
        self, date: str, puid: str, access_token: str
    ) -> Dict[str, Any]:
        """Get hourly power consumption."""
        try:
            params = {"date": date, "puid": puid}

            response = await self._api_request(
                "POST", "/clife-svc/pu/get_hour_power", data=params, access_token=access_token
            )

            if response.get("resultCode") == 0:
                return {
                    "success": True,
                    "status": response.get("powerConsumption", {}),
                }
            else:
                error_msg = response.get("msg", "Unknown error")
                raise ConnectLifeCloudAPIError(f"Failed to get hour power: {error_msg}")

        except Exception as err:
            raise ConnectLifeCloudError(f"Failed to get hour power: {err}")

    async def get_self_check(self, no_record: str, puid: str, access_token: str) -> Dict[str, Any]:
        """Get device self-check information."""
        try:
            params = {"noRecord": no_record, "puid": puid}

            response = await self._api_request(
                "POST", "/basic/self_check/info", data=params, access_token=access_token
            )

            if response.get("resultCode") == 0:
                return {
                    "success": True,
                    "status": response.get("data", {}),
                }
            else:
                error_msg = response.get("msg", "Unknown error")
                raise ConnectLifeCloudAPIError(f"Failed to get self check: {error_msg}")

        except Exception as err:
            raise ConnectLifeCloudError(f"Failed to get self check: {err}")

    def register_status_callback(
        self, device_id: str, callback: Callable[[Dict[str, Any]], None]
    ) -> None:
        """Register a callback for device status updates."""
        self._status_callbacks[device_id] = callback

    def _handle_status_update(self, device_id: str, properties: Dict[str, Any]) -> None:
        """Handle status update from WebSocket."""
        if callback := self._status_callbacks.get(device_id):
            callback(properties)

    async def get_devices_with_parsers(
        self, access_token: str
    ) -> Dict[str, tuple[DeviceInfo, BaseDeviceParser]]:
        """Get list of devices with their parsers.

        Args:
            access_token: OAuth2 access token

        Returns:
            Dictionary mapping device_id to tuple of (DeviceInfo, parser)
        """
        _LOGGER.debug("Fetching device list with parsers")

        try:
            response = await self._api_request(
                "GET", "/clife-svc/pu/get_device_status_list", access_token=access_token
            )

            if not response:
                return {}

            devices_with_parsers = {}
            device_list = response.get("deviceList", [])
            _LOGGER.debug("Found %d devices in response", len(device_list))

            for device_data in device_list:
                device_type_code = device_data.get("deviceTypeCode")
                device_feature_code = device_data.get("deviceFeatureCode")

                supported_device_types = ["009", "008", "007", "006", "016", "035"]
                if device_type_code not in supported_device_types:
                    _LOGGER.debug("Skipping unsupported device type: %s", device_type_code)
                    continue

                device = DeviceInfo.from_api_data(device_data)
                self._devices[device.device_id] = device

                # Get property list
                property_response = await self.get_property_list(
                    device_type_code, device_feature_code, access_token
                )
                property_list = property_response.get("status", [])

                # Get static data for feature code 99 devices
                if "99" in device_feature_code:
                    static_response = await self.query_static_data(device.puid, access_token)
                    self._static_data[device.device_id] = static_response.get("status", {})

                # Get device parser class and instantiate
                parser_class = get_device_parser(device_type_code, device_feature_code)
                parser = parser_class()

                # Apply filtering based on device type
                if isinstance(parser, BaseBeanParser) and not isinstance(
                    parser, (SplitWater035699Parser, Split006299Parser)
                ):
                    filtered_parser = DeviceParserFactory.create_filtered_parser(
                        parser, property_list
                    )
                    self._parsers[device.device_id] = filtered_parser

                elif isinstance(parser, SplitWater035699Parser):
                    # Check if zone 2 is available
                    if device.status.get("f_zone2_select") == "0":
                        # Create a new parser object without zone 2 attributes
                        new_parser = SplitWater035699Parser()
                        for key, value in parser.attributes.items():
                            if key not in ["f_zone2water_temp2", "t_zone2water_settemp2"]:
                                new_parser.attributes[key] = value
                        parser = new_parser

                    self._parsers[device.device_id] = parser

                elif isinstance(parser, Humidity007Parser):
                    filtered_parser = DeviceParserFactory.create_humidity_parser(
                        parser, property_list
                    )
                    self._parsers[device.device_id] = filtered_parser

                elif isinstance(parser, Split006299Parser):
                    self._parsers[device.device_id] = parser

                else:
                    _LOGGER.warning("Unknown parser type for device %s", device.device_id)
                    continue

                # Handle power consumption
                has_power = self._check_power_support(
                    device_type_code, device_feature_code, property_list, device.device_id
                )

                if has_power:
                    # Power consumption will be updated separately
                    pass
                else:
                    self._parsers[device.device_id].remove_attribute("f_power_consumption")

                devices_with_parsers[device.device_id] = (device, self._parsers[device.device_id])

                _LOGGER.debug("Added device %s with parser", device.device_id)

            return devices_with_parsers

        except Exception as err:
            _LOGGER.error("Failed to fetch devices with parsers: %s", err)
            raise ConnectLifeCloudError(f"Error communicating with API: {err}")

    def _check_power_support(
        self,
        device_type_code: str,
        device_feature_code: str,
        property_list: List[Dict[str, Any]],
        device_id: str,
    ) -> bool:
        """Check if device supports power monitoring.

        Args:
            device_type_code: Device type code
            device_feature_code: Device feature code
            property_list: List of device properties
            device_id: Device ID

        Returns:
            True if device supports power monitoring
        """
        property_keys = {
            prop.get("propertyKey") for prop in property_list if "propertyKey" in prop
        }

        if device_type_code == "009":  # Split AC
            if "99" not in device_feature_code:
                target_keys = {"f_power_display", "f_cool_qvalue", "f_heat_qvalue"}
                return bool(target_keys & property_keys)
            else:
                static_data = self._static_data.get(device_id, {})
                return static_data.get("Power_function") == "1" or static_data.get(
                    "f_cool_or_heat_qvalue"
                ) == "1"

        elif device_type_code in ["008", "006"]:  # Window AC / Portable AC
            if "99" not in device_feature_code:
                return "f_power_display" in property_keys
            else:
                static_data = self._static_data.get(device_id, {})
                return static_data.get("Power_function") == "1"

        elif device_type_code == "007":  # Dehumidifier
            if "99" not in device_feature_code:
                return "f_power_display" in property_keys
            else:
                static_data = self._static_data.get(device_id, {})
                return static_data.get("Power_function") == "1"

        else:
            target_keys = {"f_power_display", "f_cool_qvalue", "f_heat_qvalue"}
            return bool(target_keys & property_keys)

    def parse_device_status(
        self, device_id: str, status: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse device status using the appropriate parser.

        Args:
            device_id: Device ID
            status: Raw device status

        Returns:
            Parsed device status
        """
        if device_id not in self._parsers:
            _LOGGER.warning("No parser found for device %s", device_id)
            return {}

        parser = self._parsers[device_id]
        return parser.parse_status(status)

    def get_parser(self, device_id: str) -> Optional[BaseDeviceParser]:
        """Get parser for a device.

        Args:
            device_id: Device ID

        Returns:
            Device parser or None
        """
        return self._parsers.get(device_id)

    def get_static_data(self, device_id: str) -> Dict[str, Any]:
        """Get static data for a device.

        Args:
            device_id: Device ID

        Returns:
            Static data dictionary
        """
        return self._static_data.get(device_id, {})
