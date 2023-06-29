from enum import Enum
from pydantic import BaseModel
from typing import Dict, Optional

class IoTEvent(str, Enum):
    CREATE: str
    CHANGE: str
    REQUEST: str
    DELETE: str

class ValueBaseType(str, Enum):
    STRING: str
    NUMBER: str
    BLOB: str
    XML: str

class ValueSettinsSchema(BaseModel):
    value_type: ValueBaseType
    type: str
    mapping: Optional[Dict]
    ordered_mapping: Optional[bool]
    meaningful_zero: Optional[bool]
    si_conversion: Optional[str]
    min: Optional[float]
    max: Optional[float]
    step: Optional[float]
    encoding: Optional[str]
    xsd: Optional[str]
    namespace: Optional[str]
    unit: Optional[str]

class ValueTemplate(str, Enum):
    ADDRESS_NAME: str
    ALTITUDE_M: str
    ANGLE: str
    APPARENT_POWER_VA: str
    BLOB: str
    BOOLEAN_ONOFF: str
    BOOLEAN_TRUEFALSE: str
    CITY: str
    CO2_PPM: str
    COLOR_HEX: str
    COLOR_INT: str
    COLOR_TEMPERATURE: str
    CONCENTRATION_PPM: str
    CONNECTION_STATUS: str
    COUNT: str
    COUNTRY: str
    COUNTRY_CODE: str
    CURRENT_A: str
    DISTANCE_M: str
    DURATION_MIN: str
    DURATION_MSEC: str
    DURATION_SEC: str
    EMAIL: str
    ENERGY_KWH: str
    ENERGY_MWH: str
    ENERGY_PRICE_DKK_KWH: str
    ENERGY_PRICE_DKK_MWH: str
    ENERGY_PRICE_EUR_KWH: str
    ENERGY_PRICE_EUR_MWH: str
    ENERGY_WH: str
    FREQUENCY_HZ: str
    HUMIDITY: str
    IDENTIFIER: str
    IMAGE_JPG: str
    IMAGE_PNG: str
    IMPULSE_KWH: str
    INTEGER: str
    JSON: str
    LATITUDE: str
    LOAD_CURVE_ENERGY_KWH: str
    LOAD_CURVE_ENERGY_MWH: str
    LOAD_CURVE_ENERGY_WH: str
    LONGITUDE: str
    LUMINOSITY_LX: str
    NUMBER: str
    ORGANIZATION: str
    PERCENTAGE: str
    PHONE: str
    POSTCODE: str
    POWER_KW: str
    POWER_WATT: str
    PRECIPITATION_MM: str
    PRESSURE_HPA: str
    REACTIVE_ENERGY_KVARH: str
    REACTIVE_POWER_KVAR: str
    SPEED_KMH: str
    SPEED_MS: str
    STREET: str
    STRING: str
    TEMPERATURE_CELSIUS: str
    TEMPERATURE_FAHRENHEIT: str
    TEMPERATURE_KELVIN: str
    TIMESTAMP: str
    TIME_OF_DAY: str
    TOTAL_ENERGY_KWH: str
    TOTAL_ENERGY_MWH: str
    TOTAL_ENERGY_WH: str
    TRIGGER: str
    UNIT_TIME: str
    VOLTAGE_V: str
    VOLUME_M3: str
    XML: str

valueSettings: Dict[ValueTemplate, ValueSettinsSchema]
