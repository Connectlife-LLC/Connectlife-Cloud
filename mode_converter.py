"""Mode string converter for Home Assistant compatibility.

This module provides utilities to convert device mode descriptions (Chinese or English)
to standard Home Assistant strings for HVAC modes and fan modes.
"""

from __future__ import annotations

from typing import Optional


def convert_mode_to_ha_string(mode_description: str) -> Optional[str]:
    """Convert HVAC mode description to Home Assistant standard string.
    
    Args:
        mode_description: Mode description from device (can be Chinese or English)
        
    Returns:
        Standard HA HVAC mode string ("auto", "cool", "heat", "dry", "fan_only", "off")
        or None if not recognized
    """
    mode_lower = mode_description.lower()
    
    # Check for Chinese descriptions first
    if "自动" in mode_description or "auto" in mode_lower:
        return "auto"
    elif "制冷" in mode_description or "cool" in mode_lower:
        return "cool"
    elif "制热" in mode_description or "heat" in mode_lower:
        return "heat"
    elif "除湿" in mode_description or "dry" in mode_lower:
        return "dry"
    elif "送风" in mode_description or "fan" in mode_lower:
        return "fan_only"
    elif "关" in mode_description or "off" in mode_lower:
        return "off"
    
    return None


def convert_fan_mode_to_ha_string(fan_description: str) -> Optional[str]:
    """Convert fan mode description to Home Assistant standard string.
    
    Args:
        fan_description: Fan mode description from device (can be Chinese or English)
        
    Returns:
        Standard HA fan mode string ("auto", "low", "medium", "high", "medium_low", "medium_high", "ultra_low", "ultra_high")
        or None if not recognized
    """
    fan_lower = fan_description.lower()
    
    # Check for Chinese descriptions first
    if "自动" == fan_description or "auto" == fan_lower:
        return "auto"
    elif "超低" == fan_description or "ultra low" in fan_lower:
        return "ultra_low"
    elif "低" == fan_description or "low" == fan_lower:
        return "low"
    elif "中" == fan_description or "medium" == fan_lower or "med" == fan_lower:
        return "medium"
    elif "高" == fan_description or "high" == fan_lower:
        return "high"
    elif "超高" == fan_description or "ultra high" in fan_lower:
        return "ultra_high"
    # Check for medium variants (might be in the description)
    elif "medium_low" in fan_lower or "medium low" in fan_lower:
        return "medium_low"
    elif "medium_high" in fan_lower or "medium high" in fan_lower:
        return "medium_high"
    
    return None


def get_ha_mode_string(value_map: dict[str, str], device_value: str) -> Optional[str]:
    """Get HA HVAC mode string from device value map.
    
    Args:
        value_map: Device attribute value_map
        device_value: Device mode value (e.g., "0", "1", "2")
        
    Returns:
        Standard HA HVAC mode string or None
    """
    if device_value not in value_map:
        return None
    
    mode_description = value_map[device_value]
    return convert_mode_to_ha_string(mode_description)


def get_ha_fan_mode_string(value_map: dict[str, str], device_value: str) -> Optional[str]:
    """Get HA fan mode string from device value map.
    
    Args:
        value_map: Device attribute value_map
        device_value: Device fan mode value (e.g., "0", "1", "2")
        
    Returns:
        Standard HA fan mode string or None
    """
    if device_value not in value_map:
        return None
    
    fan_description = value_map[device_value]
    return convert_fan_mode_to_ha_string(fan_description)


def find_device_value_for_ha_mode(
    value_map: dict[str, str], ha_mode_string: str
) -> Optional[str]:
    """Find device value that maps to a given HA mode string.
    
    This is a reverse lookup: given an HA mode string, find the device value.
    
    Args:
        value_map: Device attribute value_map
        ha_mode_string: HA mode string (e.g., "auto", "cool", "heat")
        
    Returns:
        Device value (key) that maps to the HA mode, or None if not found
    """
    for key, value in value_map.items():
        ha_mode = convert_mode_to_ha_string(value)
        if ha_mode == ha_mode_string:
            return key
    return None


def find_device_value_for_ha_fan_mode(
    value_map: dict[str, str], ha_fan_mode_string: str
) -> Optional[str]:
    """Find device value that maps to a given HA fan mode string.
    
    This is a reverse lookup: given an HA fan mode string, find the device value.
    
    Args:
        value_map: Device attribute value_map
        ha_fan_mode_string: HA fan mode string (e.g., "auto", "low", "medium")
        
    Returns:
        Device value (key) that maps to the HA fan mode, or None if not found
    """
    for key, value in value_map.items():
        ha_fan_mode = convert_fan_mode_to_ha_string(value)
        if ha_fan_mode == ha_fan_mode_string:
            return key
    return None

