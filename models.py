"""Data models for ConnectLife Cloud API."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

_LOGGER = logging.getLogger(__name__)


@dataclass
class DeviceInfo:
    """Device information model."""

    device_id: str
    puid: str
    name: str
    type_code: str
    feature_code: str
    feature_name: str
    status: Dict[str, Any] = field(default_factory=dict)
    failed_data: List[str] = field(default_factory=list)
    static_data: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api_data(cls, data: Dict[str, Any]) -> DeviceInfo:
        """Create DeviceInfo from API response data."""
        return cls(
            device_id=data.get("deviceId", ""),
            puid=data.get("puid", ""),
            name=data.get("deviceName", ""),
            type_code=data.get("deviceTypeCode", ""),
            feature_code=data.get("deviceFeatureCode", ""),
            feature_name=data.get("deviceFeatureName", ""),
            status=data.get("statusList", {}),
            failed_data=data.get("failedData", []),
            static_data=data.get("staticData", {}),
        )

    def get_device_type(self) -> Optional[tuple[str, str]]:
        """Get device type tuple (type_code, feature_code)."""
        if self.type_code and self.feature_code:
            return (self.type_code, self.feature_code)
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "deviceId": self.device_id,
            "puid": self.puid,
            "deviceName": self.name,
            "deviceTypeCode": self.type_code,
            "deviceFeatureCode": self.feature_code,
            "deviceFeatureName": self.feature_name,
            "statusList": self.status,
            "failedData": self.failed_data,
            "staticData": self.static_data,
        }

    def debug_info(self) -> str:
        """Get debug information."""
        return f"""
Device ID: {self.device_id}
PUID: {self.puid}
Name: {self.name}
Type: {self.type_code}-{self.feature_code}
Feature Name: {self.feature_name}
Status Keys: {list(self.status.keys())}
Failed Data: {self.failed_data}
        """.strip()


@dataclass
class DeviceStatus:
    """Device status model."""

    device_id: str
    properties: Dict[str, Any] = field(default_factory=dict)
    online: bool = True
    last_update: Optional[str] = None

    def update_properties(self, properties: Dict[str, Any]) -> None:
        """Update device properties."""
        self.properties.update(properties)

    def set_online(self, online: bool) -> None:
        """Set online status."""
        self.online = online
