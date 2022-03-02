from enum import Enum

from typing import Optional
from typing import Dict

from pydantic import BaseModel


# #############################################################################
#                             Value Settings Schema
# #############################################################################

class IoTEvent(str, Enum):
    CREATE = "create"  # POST
    CHANGE = "change"  # PUT
    REQUEST = "request"  # GET
    DELETE = "delete"  # DELETE


class ValueBaseType(str, Enum):
    """Internal use only!."""
    STRING = "string"
    NUMBER = "number"
    BLOB = "blob"
    XML = "xml"


class ValueSettinsSchema(BaseModel):
    value_type: ValueBaseType
    type: str
    mapping: Optional[Dict]  # Number only
    ordered_mapping: Optional[bool]  # Number only
    meaningful_zero: Optional[bool]  # Number only
    si_conversion: Optional[str]  # Number only
    min: Optional[float]  # Number only
    max: Optional[float]  # Blob, number, str only.
    step: Optional[float]  # Number only
    encoding: Optional[str]  # Blob, str only.
    xsd: Optional[str]  # XML only
    namespace: Optional[str]  # XML only
    unit: Optional[str]  # Number only


class ValueTemplate(str, Enum):
    """
    Predefined ValueTypes.

    Each of the predefined ValueTypes, have default
    value parameters set, which include BaseType, name,
    permission, range, step and the unit.
    """

    __version__ = "0.0.1"

    ANGLE = "ANGLE"
    BLOB = "BLOB"
    BOOLEAN_ONOFF = "BOOLEAN_ONOFF"
    CITY = "CITY"
    CO2 = "CO2"
    COLOR_HEX = "COLOR_HEX"
    COLOR_INT = "COLOR_INT"
    COLOR_TEMPERATURE = "COLOR_TEMPERATURE"
    COUNTRY = "COUNTRY"
    COUNTRY_CODE = "COUNTRY_CODE"
    ENERGY_KWH = "ENERGY_KWH"
    ENERGY_WH = "ENERGY_WH"
    HUMIDITY = "HUMIDITY"
    IMAGE_JPG = "IMAGE_JPG"
    LATITUDE = "LATITUDE"
    LONGITUDE = "LONGITUDE"
    LUMINOUSITY_LX = "LUMINOUSITY_LX"
    NUMBER = "NUMBER"
    PERCENTAGE = "PERCENTAGE"
    POSTCODE = "POSTCODE"
    POWER_KW = "POWER_KW"
    POWER_WATT = "POWER_WATT"
    PRECIPITATION_MM = "PRECIPITATION_MM"
    PRESSURE_HPA = "PRESSURE_HPA"
    SPEED_MS = "SPEED_MS"
    STREET = "STREET"
    STRING = "STRING"
    TEMPERATURE_CELSIUS = "TEMPERATURE_CELSIUS"
    TEMPERATURE_FAHRENHEIT = "TEMPERATURE_FAHRENHEIT"
    TEMPERATURE_KELVIN = "TEMPERATURE_KELVIN"
    TIMESTAMP = "TIMESTAMP"
    VOLTAGE_V = "VOLTAGE_V"
    XML = "XML"


valueSettings: Dict[ValueTemplate, ValueSettinsSchema] = {

    ValueTemplate.BOOLEAN_ONOFF: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="boolean",
        mapping={'0': 'off', '1': 'on'},
        ordered_mapping=None,
        meaningful_zero=True,
        min="0",
        max="1",
        step="1",
        unit=None,
        si_conversion=None,
    ),
    ValueTemplate.VOLTAGE_V: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="voltage",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=None,
        min="0",
        max="250",
        step="1",
        unit="V",
        si_conversion=None,
    ),
    ValueTemplate.POWER_WATT: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="power",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=None,
        min="0",
        max="2500",
        step="1",
        unit="W",
        si_conversion=None,
    ),
    ValueTemplate.POWER_KW: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="power",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=None,
        min="0",
        max="1000000",
        step="1",
        unit="kW",
        si_conversion="[W] = 1000 * [kW]",
    ),
    ValueTemplate.ENERGY_WH: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="energy",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=None,
        min="0",
        max="100000",
        step="1",
        unit="Wh",
        si_conversion=None,
    ),
    ValueTemplate.ENERGY_KWH: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="energy",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=None,
        min="0",
        max="1000000",
        step="1",
        unit="kWh",
        si_conversion="[J] = 3600000 * [kWh]  ",
    ),
    ValueTemplate.TEMPERATURE_CELSIUS: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="temperature",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=False,
        min="-30",
        max="50",
        step="1",
        unit="°C",
        si_conversion="[K] = [°C] + 273.15",
    ),
    ValueTemplate.TEMPERATURE_FAHRENHEIT: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="temperature",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=False,
        min="-20",
        max="120",
        step="1",
        unit="°F",
        si_conversion="[K] = ([°F] + 459.67) × 5/9 ",
    ),
    ValueTemplate.TEMPERATURE_KELVIN: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="temperature",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=True,
        min="240",
        max="320",
        step="1",
        unit="K",
        si_conversion=None,
    ),
    ValueTemplate.ANGLE: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="angle",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=None,
        min="0",
        max="360",
        step="0",
        unit="°",
        si_conversion="[rad] = (180/pi) * [°]",
    ),
    ValueTemplate.PERCENTAGE: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="percentage",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=None,
        min="0",
        max="100",
        step="1",
        unit="%",
        si_conversion="[1] = 100 * [%]",
    ),
    ValueTemplate.SPEED_MS: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="speed",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=None,
        min="0",
        max="100",
        step="1",
        unit="m/s",
        si_conversion=None,
    ),
    ValueTemplate.PRECIPITATION_MM: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="precipitation",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=None,
        min="0",
        max="100",
        step="1",
        unit="mm",
        si_conversion=None,
    ),
    ValueTemplate.HUMIDITY: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="relative_humidity",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=True,
        min="0",
        max="100",
        step="1",
        unit="%",
        si_conversion="[1] = 100 * [%]",
    ),
    ValueTemplate.CO2: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="concentration",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=True,
        min="0",
        max="3000",
        step="1",
        unit="ppm",
        si_conversion="1000000 * [ppm]",
    ),
    ValueTemplate.PRESSURE_HPA: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="pressure",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=None,
        min="300",
        max="1100",
        step="1",
        unit="hPa",
        si_conversion="[Pa] = [hPa]/100",
    ),
    ValueTemplate.TIMESTAMP: ValueSettinsSchema(
        value_type=ValueBaseType.STRING,
        type="timestamp",
        max="27",
        encoding="ISO 8601",
    ),
    ValueTemplate.LUMINOUSITY_LX: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="luminousity",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=None,
        min="0",
        max="25000",
        step="1",
        unit="lx",
        si_conversion=None,
    ),
    ValueTemplate.COLOR_HEX: ValueSettinsSchema(
        value_type=ValueBaseType.BLOB,
        type="color",
        max="6",
        encoding="hex",
    ),
    ValueTemplate.COLOR_INT: ValueSettinsSchema(
        value_type=ValueBaseType.BLOB,
        type="color",
        max="8",
        encoding="integer",
    ),
    ValueTemplate.COLOR_TEMPERATURE: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="color_temperature",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=None,
        min="1000",
        max="12000",
        step="1",
        unit="K",
        si_conversion=None,
    ),
    ValueTemplate.IMAGE_JPG: ValueSettinsSchema(
        value_type=ValueBaseType.BLOB,
        type="image",
        max="255",
        encoding="base64",
    ),
    ValueTemplate.LATITUDE: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="latitude",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=None,
        min="-90",
        max="90",
        step="0.000001",
        unit="°N",
        si_conversion=None,
    ),
    ValueTemplate.LONGITUDE: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="longitude",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=None,
        min="-180",
        max="180",
        step="0.000001",
        unit="°E",
        si_conversion=None,
    ),
    ValueTemplate.STREET: ValueSettinsSchema(
        value_type=ValueBaseType.STRING,
        type="street",
        max="100",
        encoding="",
    ),
    ValueTemplate.CITY: ValueSettinsSchema(
        value_type=ValueBaseType.STRING,
        type="city",
        max="100",
        encoding="",
    ),
    ValueTemplate.POSTCODE: ValueSettinsSchema(
        value_type=ValueBaseType.STRING,
        type="postcode",
        max="10",
        encoding="",
    ),
    ValueTemplate.COUNTRY: ValueSettinsSchema(
        value_type=ValueBaseType.STRING,
        type="country",
        max="20",
        encoding="",
    ),
    ValueTemplate.COUNTRY_CODE: ValueSettinsSchema(
        value_type=ValueBaseType.STRING,
        type="country_code",
        max="2",
        encoding="ISO 3166-1 Alpha-2",
    ),
    ValueTemplate.NUMBER: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="number",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=None,
        min="-128",
        max="128",
        step="0.1",
        unit=None,
        si_conversion=None,
    ),
    ValueTemplate.STRING: ValueSettinsSchema(
        value_type=ValueBaseType.STRING,
        type="string",
        max="64",
        encoding="utf-8",
    ),
    ValueTemplate.BLOB: ValueSettinsSchema(
        value_type=ValueBaseType.BLOB,
        type="blob",
        max="280",
        encoding="base64",
    ),
    ValueTemplate.XML: ValueSettinsSchema(
        value_type=ValueBaseType.XML,
        type="xml",
        xsd="",
        namespace="",
    ),
}
