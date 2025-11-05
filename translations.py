"""Translation management for ConnectLife devices."""

from __future__ import annotations

import logging
from typing import Dict, Optional

_LOGGER = logging.getLogger(__name__)


class TranslationManager:
    """Manages translations for device attributes and states."""

    SUPPORTED_LANGUAGES = ["en", "zh-Hans"]

    TRANSLATIONS = {
        "zh-Hans": {
            "indoor_temperature": "室内温度",
            "power_consumption": "能耗",
            "indoor_humidity": "室内湿度",
            "in_water_temp": "进水口温度",
            "out_water_temp": "出水口温度",
            "f_zone1water_temp1": "温区1实际值",
            "f_zone2water_temp2": "温区2实际值",
            "f_e_intemp": "室内温度传感器故障",
            "f_e_incoiltemp": "室内盘管温度传感器故障",
            "f_e_inhumidity": "室内湿度传感器故障",
            "f_e_infanmotor": "室内风机电机运转异常故障",
            "f_e_arkgrille": "柜机格栅保护告警",
            "f_e_invzero": "室内电压过零检测故障",
            "f_e_incom": "室内外通信故障",
            "f_e_indisplay": "室内控制板与显示板通信故障",
            "f_e_inkeys": "室内控制板与按键板通信故障",
            "f_e_inwifi": "WIFI控制板与室内控制板通信故障",
            "f_e_inele": "室内控制板与室内电量板通信故障",
            "f_e_ineeprom": "室内控制板EEPROM出错",
            "f_e_outeeprom": "室外EEPROM出错",
            "f_e_outcoiltemp": "室外盘管温度传感器故障",
            "f_e_outgastemp": "排气温度传感器故障",
            "f_e_outtemp": "室外环境温度传感器故障",
            "f_e_push": "推送故障",
            "f_e_waterfull": "水满报警",
            "f_e_upmachine": "室内（上部）直流风机电机运转异常故障",
            "f_e_dwmachine": "室外（下部）直流风机电机运转异常故障",
            "f_e_filterclean": "过滤网清洁告警",
            "f_e_wetsensor": "湿敏传感器故障",
            "f_e_tubetemp": "管温传感器故障",
            "f_e_temp": "室温传感器故障",
            "f_e_pump": "水泵故障",
            "f_e_exhaust_hightemp": "排气温度过高",
            "f_e_high_pressure": "高压故障",
            "f_e_low_pressure": "低压故障",
            "f_e_wire_drive": "通信故障",
            "f_e_coiltemp": "盘管温度传感器故障",
            "f_e_env_temp": "环境温度传感器故障",
            "f_e_exhaust": "排气温度传感器故障",
            "f_e_inwater": "进水温度传感器故障",
            "f_e_water_tank": "水箱温度传感器故障",
            "f_e_return_air": "回气温度传感器故障",
            "f_e_outwater": "出水温度传感器故障",
            "f_e_solar_temperature": "太阳能温度传感器故障",
            "f_e_compressor_overload": "压缩机过载",
            "f_e_excessive_current": "电流过大",
            "f_e_fan_fault": "风机故障",
            "f_e_displaycom_fault": "显示板通信故障",
            "f_e_upwatertank_fault": "水箱上部温度传感器故障",
            "f_e_downwatertank_fault": "水箱下部温度传感器故障",
            "f_e_suctiontemp_fault": "吸气温度传感器故障",
            "f_e_e2data_fault": "EEPROM数据故障",
            "f_e_drivecom_fault": "驱动板通信故障",
            "f_e_drive_fault": "驱动板故障",
            "f_e_returnwatertemp_fault": "回水温度传感器故障",
            "f_e_clockchip_fault": "时钟芯片故障",
            "f_e_eanode_fault": "电子阳极故障",
            "f_e_powermodule_fault": "电量模块故障",
            "f_e_fan_fault_tip": "外风机故障",
            "f_e_pressuresensor_fault_tip": "压力传感器故障",
            "f_e_tempfault_solarwater_tip": "太阳能水温感温故障",
            "f_e_tempfault_mixedwater_tip": "混水感温故障",
            "f_e_tempfault_balance_watertank_tip": "平衡水箱感温故障",
            "f_e_tempfault_eheating_outlet_tip": "内置电加热出水感温故障",
            "f_e_tempfault_refrigerant_outlet_tip": "冷媒出口温感故障",
            "f_e_tempfault_refrigerant_inlet_tip": "冷媒进口温感故障",
            "f_e_inwaterpump_tip": "内置水泵故障",
            "f_e_outeeprom_tip": "外机EEPROM故障",
            "quiet_mode": "静音模式",
            "rapid_mode": "快速制热/制冷",
            "8heat_mode": "8度制热模式",
            "eco_mode": "节能",
            "fan_speed_自动": "自动风",
            "fan_speed_中风": "中速",
            "fan_speed_高风": "高速",
            "fan_speed_低风": "低速",
            "t_zone1water_settemp1": "1温区设置值",
            "t_zone2water_settemp2": "2温区设置值",
            "STATE_CONTINUOUS": "持续",
            "STATE_NORMAL": "手动",
            "STATE_AUTO": "自动",
            "STATE_DRY": "干衣",
            "STATE_OFF": "关闭",
            "STATE_ELECTRIC": "电加热",
            "STATE_DUAL_MODE": "双能模式",
            "STATE_DUAL_MODE_": "双能",
            "STATE_DUAL_1": "快",
            "STATE_DUAL_1_": "双能1",
            "STATE_HEAT": "制热",
            "STATE_COOL": "制冷",
            "STATE_HOT_WATER_COOL": "制冷+生活热水",
            "STATE_HOT_WATER_AUTO": "自动+生活热水",
            "STATE_HOT_WATER": "仅生活热水",
            "STATE_HOT_WATER_HEAT": "制热+生活热水",
            "fan_speed_ultra_low": "中低",
            "fan_speed_ultra_high": "中高",
            "fan_speed_low": "低",
            "fan_speed_high": "高",
        },
        "en": {
            "indoor_temperature": "Indoor Temperature",
            "power_consumption": "Power Consumption",
            "indoor_humidity": "Indoor Humidity",
            "in_water_temp": "In Water Temp",
            "out_water_temp": "Out Water Temp",
            "f_zone1water_temp1": "Zone 1 Actual Temp",
            "f_zone2water_temp2": "Zone 2 Actual Temp",
            "f_e_intemp": "Indoor Temperature Sensor Fault",
            "f_e_incoiltemp": "Indoor Coil Temperature Sensor Fault",
            "f_e_inhumidity": "Indoor Humidity Sensor Fault",
            "f_e_infanmotor": "Indoor Fan Motor Fault",
            "f_e_arkgrille": "Cabinet Grill Protection Alert",
            "f_e_invzero": "Indoor Zero Voltage Detection Fault",
            "f_e_incom": "Indoor-Outdoor Communication Fault",
            "f_e_indisplay": "Indoor Display Board Communication Fault",
            "f_e_inkeys": "Indoor Key Panel Communication Fault",
            "f_e_inwifi": "WiFi Control Board Communication Fault",
            "f_e_inele": "Indoor Power Board Communication Fault",
            "f_e_ineeprom": "Indoor EEPROM Error",
            "f_e_outeeprom": "Outdoor EEPROM Error",
            "f_e_outcoiltemp": "Outdoor Coil Temperature Sensor Fault",
            "f_e_outgastemp": "Exhaust Temperature Sensor Fault",
            "f_e_outtemp": "Outdoor Ambient Temperature Sensor Fault",
            "f_e_push": "Push Notification Fault",
            "f_e_waterfull": "Tank Full Alert",
            "f_e_upmachine": "Upper Indoor Fan Fault",
            "f_e_dwmachine": "Lower Outdoor Fan Fault",
            "f_e_filterclean": "Filter Clean Alert",
            "f_e_wetsensor": "Moisture Sensor Fault",
            "f_e_tubetemp": "Pipe Temperature Sensor Fault",
            "f_e_temp": "Room Temperature Sensor Fault",
            "f_e_pump": "Pump Fault",
            "f_e_exhaust_hightemp": "Exhaust Overheating",
            "f_e_high_pressure": "High Pressure Fault",
            "f_e_low_pressure": "Low Pressure Fault",
            "f_e_wire_drive": "Communication Fault",
            "f_e_coiltemp": "Coil Temperature Sensor Fault",
            "f_e_env_temp": "Environmental Temperature Sensor Fault",
            "f_e_exhaust": "Exhaust Temperature Sensor Fault",
            "f_e_inwater": "Inlet Water Temperature Sensor Fault",
            "f_e_water_tank": "Tank Temperature Sensor Fault",
            "f_e_return_air": "Return Air Temperature Sensor Fault",
            "f_e_outwater": "Outlet Water Temperature Sensor Fault",
            "f_e_solar_temperature": "Solar Temperature Sensor Fault",
            "f_e_compressor_overload": "Compressor Overload",
            "f_e_excessive_current": "Overcurrent",
            "f_e_fan_fault": "Fan Fault",
            "f_e_displaycom_fault": "Display Board Communication Fault",
            "f_e_upwatertank_fault": "Upper Tank Temperature Sensor Fault",
            "f_e_downwatertank_fault": "Lower Tank Temperature Sensor Fault",
            "f_e_suctiontemp_fault": "Suction Temperature Sensor Fault",
            "f_e_e2data_fault": "EEPROM Data Fault",
            "f_e_drivecom_fault": "Drive Board Communication Fault",
            "f_e_drive_fault": "Drive Board Fault",
            "f_e_returnwatertemp_fault": "Return Water Temperature Sensor Fault",
            "f_e_clockchip_fault": "Clock Chip Fault",
            "f_e_eanode_fault": "Anode Fault",
            "f_e_powermodule_fault": "Power Module Fault",
            "f_e_fan_fault_tip": "Outdoor Fan Fault",
            "f_e_pressuresensor_fault_tip": "Pressure Sensor Fault",
            "f_e_tempfault_solarwater_tip": "Solar Water Sensor Fault",
            "f_e_tempfault_mixedwater_tip": "Mixed Water Sensor Fault",
            "f_e_tempfault_balance_watertank_tip": "Balance Tank Sensor Fault",
            "f_e_tempfault_eheating_outlet_tip": "Electric Heater Outlet Sensor Fault",
            "f_e_tempfault_refrigerant_outlet_tip": "Refrigerant Outlet Sensor Fault",
            "f_e_tempfault_refrigerant_inlet_tip": "Refrigerant Inlet Sensor Fault",
            "f_e_inwaterpump_tip": "Pump Fault",
            "f_e_outeeprom_tip": "Outdoor EEPROM Fault",
            "quiet_mode": "Quiet Mode",
            "rapid_mode": "Fast Heating/Cooling",
            "8heat_mode": "8 Heat Mode",
            "eco_mode": "Eco",
            "fan_speed_自动": "Auto speed",
            "fan_speed_中风": "Medium",
            "fan_speed_高风": "High",
            "fan_speed_低风": "Low",
            "t_zone1water_settemp1": "Zone 1 Set Temp",
            "t_zone2water_settemp2": "Zone 2 Set Temp",
            "STATE_CONTINUOUS": "Continuous",
            "STATE_NORMAL": "Manual",
            "STATE_AUTO": "Auto",
            "STATE_DRY": "Clothes dry",
            "STATE_OFF": "Off",
            "STATE_ELECTRIC": "Electric heating",
            "STATE_DUAL_MODE": "Dual Mode",
            "STATE_DUAL_MODE_": "Boost",
            "STATE_DUAL_1": "Fast",
            "STATE_DUAL_1_": "Boost1",
            "STATE_HEAT": "Heat",
            "STATE_COOL": "Cool",
            "STATE_HOT_WATER_COOL": "Cool & DHW",
            "STATE_HOT_WATER_AUTO": "Auto & DHW",
            "STATE_HOT_WATER": "only DHW",
            "STATE_HOT_WATER_HEAT": "Heat & DHW",
            "fan_speed_ultra_low": "Ultra Low",
            "fan_speed_ultra_high": "Ultra High",
            "fan_speed_low": "Low",
            "fan_speed_high": "High",
        },
    }

    @classmethod
    def get_translation(
        cls, key: str, language: str = "en", default: Optional[str] = None
    ) -> str:
        """Get translation for a key in the specified language.

        Args:
            key: Translation key
            language: Language code (en, zh-Hans)
            default: Default value if translation not found

        Returns:
            Translated string or default value
        """
        if language not in cls.SUPPORTED_LANGUAGES:
            _LOGGER.warning("Unsupported language: %s, falling back to 'en'", language)
            language = "en"

        translations = cls.TRANSLATIONS.get(language, cls.TRANSLATIONS["en"])
        return translations.get(key, default or key)

    @classmethod
    def get_all_translations(cls, language: str = "en") -> Dict[str, str]:
        """Get all translations for a language.

        Args:
            language: Language code

        Returns:
            Dictionary of translations
        """
        if language not in cls.SUPPORTED_LANGUAGES:
            language = "en"

        return cls.TRANSLATIONS.get(language, cls.TRANSLATIONS["en"])

