"""ConnectLife Cloud API client library for Home Assistant integrations."""

from .client import ConnectLifeCloudClient
from .device_manager import DeviceParserFactory
from .exceptions import (
    ConnectLifeCloudAuthError,
    ConnectLifeCloudConnectionError,
    ConnectLifeCloudError,
)
from .models import DeviceInfo, DeviceStatus
from .translations import TranslationManager

# Import device classes
from .devices import get_device_parser
from .devices.atw_035_699 import SplitWater035699Parser
from .devices.base import BaseDeviceParser
from .devices.bean_006_299 import Split006299Parser
from .devices.hum_007 import Humidity007Parser
from .devices.split_ac_009_199 import SplitAC009199Parser
from .devices.window_ac_008_399 import WindowAC008399Parser

__version__ = "0.3.0"
__all__ = [
    "ConnectLifeCloudClient",
    "ConnectLifeCloudError",
    "ConnectLifeCloudAuthError",
    "ConnectLifeCloudConnectionError",
    "DeviceInfo",
    "DeviceStatus",
    "TranslationManager",
    "DeviceParserFactory",
    "BaseDeviceParser",
    "get_device_parser",
    "SplitAC009199Parser",
    "WindowAC008399Parser",
    "Split006299Parser",
    "Humidity007Parser",
    "SplitWater035699Parser",
]
