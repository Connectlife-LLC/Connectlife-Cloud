"""Device management utilities for ConnectLife Cloud."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from .devices import get_device_parser
from .devices.base import BaseDeviceParser, DeviceAttribute
from .devices.base_bean import BaseBeanParser
from .devices.hum_007 import Humidity007Parser

_LOGGER = logging.getLogger(__name__)


class DeviceParserFactory:
    """Factory for creating and filtering device parsers."""

    @staticmethod
    def create_filtered_parser(
        base_parser: BaseDeviceParser, property_list: List[Dict[str, Any]]
    ) -> BaseBeanParser:
        """Create a filtered parser based on property list from API.

        Args:
            base_parser: Base device parser instance
            property_list: List of properties from API

        Returns:
            Filtered BaseBeanParser instance
        """
        original_attributes = base_parser.attributes

        if not isinstance(original_attributes, dict):
            _LOGGER.error("original_attributes is not a dictionary: %s", original_attributes)
            return BaseBeanParser()

        # Extract propertyKey to form a new list
        property_keys = [
            prop.get("propertyKey")
            for prop in property_list
            if isinstance(prop, dict) and "propertyKey" in prop
        ]

        _LOGGER.debug("property_keys content: %s", property_keys)

        if not isinstance(property_keys, (list, set)):
            _LOGGER.error("property_keys is not a list or set: %s", property_keys)
            return BaseBeanParser()

        # Ensure elements in property_keys are hashable types
        if any(not isinstance(item, (str, int, float, tuple)) for item in property_keys):
            _LOGGER.error("property_keys contains unhashable types: %s", property_keys)
            return BaseBeanParser()

        # Create a new attributes dictionary containing only the intersection
        filtered_attributes = {}
        for key in property_keys:
            if key in original_attributes:
                attribute = original_attributes[key]
                # Update value_range
                for prop in property_list:
                    if prop.get("propertyKey") == key:
                        property_value_list = prop.get("propertyValueList")
                        if property_value_list:
                            attribute.value_range = property_value_list
                            break

                # Filter value_map
                if attribute.value_map:
                    # Convert property_value_list_keys to a set
                    property_value_list_keys = set(property_value_list.split(","))

                    # Ensure value_map_keys is a set
                    value_map_keys = set(attribute.value_map.keys())

                    # Calculate intersection
                    filtered_value_map = {
                        k: attribute.value_map[k]
                        for k in value_map_keys.intersection(property_value_list_keys)
                    }
                    attribute.value_map = filtered_value_map

                filtered_attributes[key] = attribute

        # Force add f_power_consumption field
        if "f_power_consumption" not in filtered_attributes:
            filtered_attributes["f_power_consumption"] = DeviceAttribute(
                key="f_power_consumption",
                name="Power Consumption",
                attr_type="Number",
                step=1,
                read_write="R",
            )
            _LOGGER.debug("Force added f_power_consumption field to parser")

        _LOGGER.debug("filtered_attributes content: %s", filtered_attributes)

        # Create a new BaseBeanParser object and assign filtered_attributes to its attributes
        new_parser = BaseBeanParser()
        _LOGGER.debug("Static data for filtered_parser %s", new_parser.attributes)
        new_parser._attributes = filtered_attributes

        return new_parser

    @staticmethod
    def create_humidity_parser(
        base_parser: Humidity007Parser, property_list: List[Dict[str, Any]]
    ) -> Humidity007Parser:
        """Create a filtered humidity parser based on property list from API.

        Args:
            base_parser: Humidity007Parser instance
            property_list: List of properties from API

        Returns:
            Filtered Humidity007Parser instance
        """
        original_attributes = base_parser.attributes

        if not isinstance(original_attributes, dict):
            _LOGGER.error("original_attributes is not a dictionary: %s", original_attributes)
            return Humidity007Parser()

        # Extract propertyKey to form a new list
        property_keys = [
            prop.get("propertyKey")
            for prop in property_list
            if isinstance(prop, dict) and "propertyKey" in prop
        ]

        _LOGGER.debug("property_keys content: %s", property_keys)

        if not isinstance(property_keys, (list, set)):
            _LOGGER.error("property_keys is not a list or set: %s", property_keys)
            return Humidity007Parser()

        # Ensure elements in property_keys are hashable types
        if any(not isinstance(item, (str, int, float, tuple)) for item in property_keys):
            _LOGGER.error("property_keys contains unhashable types: %s", property_keys)
            return Humidity007Parser()

        # Create a new attributes dictionary containing only the intersection
        filtered_attributes = {}
        for key in property_keys:
            if key in original_attributes:
                attribute = original_attributes[key]
                # Update value_range
                for prop in property_list:
                    if prop.get("propertyKey") == key:
                        property_value_list = prop.get("propertyValueList")
                        if property_value_list:
                            attribute.value_range = property_value_list
                            break

                # Filter value_map
                if attribute.value_map:
                    # Convert property_value_list_keys to a set
                    property_value_list_keys = set(property_value_list.split(","))

                    # Ensure value_map_keys is a set
                    value_map_keys = set(attribute.value_map.keys())

                    # Calculate intersection
                    filtered_value_map = {
                        k: attribute.value_map[k]
                        for k in value_map_keys.intersection(property_value_list_keys)
                    }
                    attribute.value_map = filtered_value_map

                filtered_attributes[key] = attribute

        _LOGGER.debug("Dehumidifier filtered_attributes content: %s", filtered_attributes)

        # Create a new Humidity007Parser object and assign filtered_attributes to its attributes
        new_parser = Humidity007Parser()
        _LOGGER.debug(
            "Dehumidifier static data for filtered_parser before %s", new_parser.attributes
        )
        new_parser._attributes = filtered_attributes
        _LOGGER.debug(
            "Dehumidifier static data for filtered_parser after %s", new_parser.attributes
        )

        return new_parser

