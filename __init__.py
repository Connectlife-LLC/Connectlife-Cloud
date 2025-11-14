"""ConnectLife Cloud API client library for Home Assistant integrations."""

from .client import ConnectLifeCloudClient
from .device_manager import DeviceParserFactory
from .exceptions import (
    ConnectLifeCloudAuthError,
    ConnectLifeCloudConnectionError,
    ConnectLifeCloudError,
)
from .mode_converter import (
    convert_fan_mode_to_ha_string,
    convert_mode_to_ha_string,
    find_device_value_for_ha_fan_mode,
    find_device_value_for_ha_mode,
    get_ha_fan_mode_string,
    get_ha_mode_string,
)
from .models import DeviceInfo, DeviceStatus, NotificationInfo, PushChannel
from .translations import TranslationManager
from .websocket import ConnectLifeWebSocket

# Import device classes
from .devices import get_device_parser
from .devices.atw_035_699 import SplitWater035699Parser
from .devices.base import BaseDeviceParser
from .devices.bean_006_299 import Split006299Parser
from .devices.hum_007 import Humidity007Parser
from .devices.split_ac_009_199 import SplitAC009199Parser
from .devices.window_ac_008_399 import WindowAC008399Parser

__version__ = "0.3.2"
__all__ = [
    "ConnectLifeCloudClient",
    "ConnectLifeCloudError",
    "ConnectLifeCloudAuthError",
    "ConnectLifeCloudConnectionError",
    "DeviceInfo",
    "DeviceStatus",
    "NotificationInfo",
    "PushChannel",
    "TranslationManager",
    "DeviceParserFactory",
    "convert_mode_to_ha_string",
    "convert_fan_mode_to_ha_string",
    "get_ha_mode_string",
    "get_ha_fan_mode_string",
    "find_device_value_for_ha_mode",
    "find_device_value_for_ha_fan_mode",
    "BaseDeviceParser",
    "get_device_parser",
    "SplitAC009199Parser",
    "WindowAC008399Parser",
    "Split006299Parser",
    "Humidity007Parser",
    "SplitWater035699Parser",
    "ConnectLifeWebSocket",
]
