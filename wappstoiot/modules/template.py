"""Contain the Value Templates for Wappsto."""
from enum import Enum

from typing import Optional
from typing import Dict

from pydantic import BaseModel


# #############################################################################
#                             Value Settings Schema
# #############################################################################

class IoTEvent(str, Enum):
    """Different IoT Event."""
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
    """The Structure for which all templates should follow."""
    value_type: ValueBaseType
    type: str
    mapping: Optional[Dict[str, str]] = None  # Number only
    ordered_mapping: Optional[bool] = None  # Number only
    meaningful_zero: Optional[bool] = None  # Number only
    si_conversion: Optional[str] = None  # Number only
    min: Optional[str] = None  # Number only
    max: Optional[str] = None  # Blob, number, str only.
    step: Optional[str] = None  # Number only
    encoding: Optional[str] = None  # Blob, str only.
    xsd: Optional[str] = None  # XML only
    namespace: Optional[str] = None  # XML only
    unit: Optional[str] = None  # Number only


class ValueTemplate(str, Enum):
    """
    Predefined ValueTemplate.

    Each of the predefined ValueTemplate, have default
    value parameters set, which include BaseType, name,
    permission, range, step and the unit.
    """
    __version__ = "0.0.5"

    ADDRESS_NAME = "ADDRESS_NAME"
    ALTITUDE_M = "ALTITUDE_M"
    ANGLE = "ANGLE"
    APPARENT_POWER_VA = "APPARENT_POWER_VA"
    BLOB = "BLOB"
    BOOLEAN_ONOFF = "BOOLEAN_ONOFF"
    BOOLEAN_TRUEFALSE = "BOOLEAN_TRUEFALSE"
    CITY = "CITY"
    CO2_PPM = "CO2_PPM"
    COLOR_HEX = "COLOR_HEX"
    COLOR_INT = "COLOR_INT"
    COLOR_TEMPERATURE = "COLOR_TEMPERATURE"
    CONCENTRATION_PPM = "CONCENTRATION_PPM"
    CONNECTION_STATUS = "CONNECTION_STATUS"
    COUNT = "COUNT"
    COUNTRY = "COUNTRY"
    COUNTRY_CODE = "COUNTRY_CODE"
    CURRENT_A = "CURRENT_A"
    DISTANCE_M = "DISTANCE_M"
    DURATION_MIN = "DURATION_MIN"
    DURATION_MSEC = "DURATION_MSEC"
    DURATION_SEC = "DURATION_SEC"
    EMAIL = "EMAIL"
    ENERGY_KWH = "ENERGY_KWH"
    ENERGY_MWH = "ENERGY_MWH"
    ENERGY_PRICE_DKK_KWH = "ENERGY_PRICE_DKK_KWH"
    ENERGY_PRICE_DKK_MWH = "ENERGY_PRICE_DKK_MWH"
    ENERGY_PRICE_EUR_KWH = "ENERGY_PRICE_EUR_KWH"
    ENERGY_PRICE_EUR_MWH = "ENERGY_PRICE_EUR_MWH"
    ENERGY_WH = "ENERGY_WH"
    FREQUENCY_HZ = "FREQUENCY_HZ"
    HUMIDITY = "HUMIDITY"
    IDENTIFIER = "IDENTIFIER"
    IMAGE_JPG = "IMAGE_JPG"
    IMAGE_PNG = "IMAGE_PNG"
    IMPULSE_KWH = "IMPULSE_KWH"
    INTEGER = "INTEGER"
    JSON = "JSON"
    LATITUDE = "LATITUDE"
    LOAD_CURVE_ENERGY_KWH = "LOAD_CURVE_ENERGY_KWH"
    LOAD_CURVE_ENERGY_MWH = "LOAD_CURVE_ENERGY_MWH"
    LOAD_CURVE_ENERGY_WH = "LOAD_CURVE_ENERGY_WH"
    LONGITUDE = "LONGITUDE"
    LUMINOSITY_LX = "LUMINOSITY_LX"
    NUMBER = "NUMBER"
    ORGANIZATION = "ORGANIZATION"
    PERCENTAGE = "PERCENTAGE"
    PHONE = "PHONE"
    POSTCODE = "POSTCODE"
    POWER_KW = "POWER_KW"
    POWER_WATT = "POWER_WATT"
    PRECIPITATION_MM = "PRECIPITATION_MM"
    PRESSURE_HPA = "PRESSURE_HPA"
    REACTIVE_ENERGY_KVARH = "REACTIVE_ENERGY_KVARH"
    REACTIVE_POWER_KVAR = "REACTIVE_POWER_KVAR"
    SPEED_KMH = "SPEED_KMH"
    SPEED_MS = "SPEED_MS"
    STREET = "STREET"
    STRING = "STRING"
    TEMPERATURE_CELSIUS = "TEMPERATURE_CELSIUS"
    TEMPERATURE_FAHRENHEIT = "TEMPERATURE_FAHRENHEIT"
    TEMPERATURE_KELVIN = "TEMPERATURE_KELVIN"
    TIMESTAMP = "TIMESTAMP"
    TIME_OF_DAY = "TIME_OF_DAY"
    TOTAL_ENERGY_KWH = "TOTAL_ENERGY_KWH"
    TOTAL_ENERGY_MWH = "TOTAL_ENERGY_MWH"
    TOTAL_ENERGY_WH = "TOTAL_ENERGY_WH"
    TRIGGER = "TRIGGER"
    UNIT_TIME = "UNIT_TIME"
    VOLTAGE_V = "VOLTAGE_V"
    VOLUME_M3 = "VOLUME_M3"
    XML = "XML"


valueSettings: Dict[ValueTemplate, ValueSettinsSchema] = {

    ValueTemplate.TRIGGER: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="trigger",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=None,
        min="0",
        max="0",
        step="0",
        unit=None,
        si_conversion=None,
    ),
    ValueTemplate.BOOLEAN_TRUEFALSE: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="boolean",
        mapping={'0': 'false', '1': 'true'},
        ordered_mapping=None,
        meaningful_zero=None,
        min="0",
        max="1",
        step="1",
        unit=None,
        si_conversion=None,
    ),
    ValueTemplate.BOOLEAN_ONOFF: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="boolean",
        mapping={'0': 'off', '1': 'on'},
        ordered_mapping=None,
        meaningful_zero=None,
        min="0",
        max="1",
        step="1",
        unit=None,
        si_conversion=None,
    ),
    ValueTemplate.CONNECTION_STATUS: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="connection",
        mapping={'0': 'offline', '1': 'online'},
        ordered_mapping=None,
        meaningful_zero=None,
        min="0",
        max="1",
        step="1",
        unit=None,
        si_conversion=None,
    ),
    ValueTemplate.INTEGER: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="integer",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=None,
        min="-255",
        max="255",
        step="1",
        unit=None,
        si_conversion=None,
    ),
    ValueTemplate.COUNT: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="count",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=None,
        min="0",
        max="255",
        step="1",
        unit=None,
        si_conversion=None,
    ),
    ValueTemplate.IMPULSE_KWH: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="impulse_resolution",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=True,
        min="1",
        max="50000",
        step="1",
        unit="imp/kWh",
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
        step="0.1",
        unit="V",
        si_conversion=None,
    ),
    ValueTemplate.POWER_WATT: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="power",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=None,
        min="-1000000",
        max="2500",
        step="0.1",
        unit="W",
        si_conversion=None,
    ),
    ValueTemplate.POWER_KW: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="power",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=None,
        min="-1000000",
        max="1000000",
        step="0.1",
        unit="kW",
        si_conversion="[W] = 1000 * [kW]",
    ),
    ValueTemplate.ENERGY_WH: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="energy",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=None,
        min="-1000000",
        max="100000",
        step="0.1",
        unit="Wh",
        si_conversion="[J] = 3600 * [Wh]",
    ),
    ValueTemplate.ENERGY_KWH: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="energy",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=None,
        min="-1000000",
        max="1000000",
        step="0.1",
        unit="kWh",
        si_conversion="[J] = 3600000 * [kWh]",
    ),
    ValueTemplate.ENERGY_MWH: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="energy",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=None,
        min="-1000000",
        max="1000000",
        step="0.1",
        unit="MWh",
        si_conversion="[J] = 3600000000 * [MWh]",
    ),
    ValueTemplate.TOTAL_ENERGY_WH: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="total_energy",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=None,
        min="0",
        max="1000000",
        step="0.1",
        unit="Wh",
        si_conversion="[J] = 3600 * [Wh]",
    ),
    ValueTemplate.TOTAL_ENERGY_KWH: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="total_energy",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=None,
        min="0",
        max="1000000",
        step="0.1",
        unit="kWh",
        si_conversion="[J] = 3600000 * [kWh]  ",
    ),
    ValueTemplate.TOTAL_ENERGY_MWH: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="total_energy",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=None,
        min="0",
        max="1000000",
        step="0.1",
        unit="MWh",
        si_conversion="[J] = 3600000000 * [MWh]",
    ),
    ValueTemplate.LOAD_CURVE_ENERGY_WH: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="load_curve_energy",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=None,
        min="-1000000",
        max="1000000",
        step="0.1",
        unit="Wh",
        si_conversion="[J] = 3600 * [Wh]",
    ),
    ValueTemplate.LOAD_CURVE_ENERGY_KWH: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="load_curve_energy",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=None,
        min="-1000000",
        max="1000000",
        step="0.1",
        unit="kWh",
        si_conversion="[J] = 3600000 * [kWh]  ",
    ),
    ValueTemplate.LOAD_CURVE_ENERGY_MWH: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="load_curve_energy",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=None,
        min="-1000000",
        max="1000000",
        step="0.1",
        unit="MWh",
        si_conversion="[J] = 3600000000 * [MWh]",
    ),
    ValueTemplate.CURRENT_A: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="electric_current",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=None,
        min="-5000",
        max="5000",
        step="0.001",
        unit="A",
        si_conversion=None,
    ),
    ValueTemplate.APPARENT_POWER_VA: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="apparent_power",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=None,
        min="-5000",
        max="5000",
        step="0.001",
        unit="VA",
        si_conversion=None,
    ),
    ValueTemplate.REACTIVE_ENERGY_KVARH: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="reactive_energy",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=None,
        min="-5000",
        max="5000",
        step="0.001",
        unit="kvarh",
        si_conversion=None,
    ),
    ValueTemplate.REACTIVE_POWER_KVAR: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="reactive_power",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=None,
        min="-5000",
        max="5000",
        step="0.001",
        unit="kvar",
        si_conversion=None,
    ),
    ValueTemplate.ENERGY_PRICE_EUR_KWH: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="energy_price",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=False,
        min="-10000",
        max="10000",
        step="0.01",
        unit="EUR/kWh",
        si_conversion=None,
    ),
    ValueTemplate.ENERGY_PRICE_EUR_MWH: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="energy_price",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=False,
        min="-10000",
        max="10000",
        step="0.001",
        unit="EUR/MWh",
        si_conversion=None,
    ),
    ValueTemplate.ENERGY_PRICE_DKK_KWH: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="energy_price",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=False,
        min="-10000",
        max="10000",
        step="0.01",
        unit="DKK/kWh",
        si_conversion=None,
    ),
    ValueTemplate.ENERGY_PRICE_DKK_MWH: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="energy_price",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=False,
        min="-10000",
        max="10000",
        step="0.001",
        unit="DKK/MWh",
        si_conversion=None,
    ),
    ValueTemplate.FREQUENCY_HZ: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="frequency",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=None,
        min="0",
        max="30000",
        step="0.01",
        unit="Hz",
        si_conversion=None,
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
    ValueTemplate.SPEED_KMH: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="speed",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=True,
        min="0",
        max="400",
        step="0.1",
        unit="km/h",
        si_conversion="[ms] = [kmh]*1000/3600",
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
    ValueTemplate.CO2_PPM: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="co2",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=True,
        min="0",
        max="3000",
        step="1",
        unit="ppm",
        si_conversion="1000000 * [ppm]",
    ),
    ValueTemplate.CONCENTRATION_PPM: ValueSettinsSchema(
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
    ValueTemplate.VOLUME_M3: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="volume",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=True,
        min="0",
        max="1000000000",
        step="0.001",
        unit="m³",
        si_conversion="[m³] = [m³]",
    ),
    ValueTemplate.UNIT_TIME: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="timestamp",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=True,
        min="0",
        max="2147483647",
        step="1",
        unit="s",
        si_conversion="[s] = [s]",
    ),
    ValueTemplate.TIMESTAMP: ValueSettinsSchema(
        value_type=ValueBaseType.STRING,
        type="timestamp",
        max="27",
        encoding="ISO 8601",
    ),
    ValueTemplate.DURATION_MIN: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="duration",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=None,
        min="0",
        max="1440",
        step="0.1",
        unit="min",
        si_conversion="[s] = [min] / 60",
    ),
    ValueTemplate.DURATION_SEC: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="duration",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=None,
        min="0",
        max="3600",
        step="0.001",
        unit="s",
        si_conversion="[s] = [s]",
    ),
    ValueTemplate.DURATION_MSEC: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="duration",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=None,
        min="0",
        max="5000",
        step="0.001",
        unit="ms",
        si_conversion="[s] = [ms]/1000",
    ),
    ValueTemplate.TIME_OF_DAY: ValueSettinsSchema(
        value_type=ValueBaseType.STRING,
        type="time",
        max="100",
        encoding="",
    ),
    ValueTemplate.DISTANCE_M: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="distance",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=None,
        min="0",
        max="1000",
        step="1",
        unit="m",
        si_conversion=None,
    ),
    ValueTemplate.LUMINOSITY_LX: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="luminosity",
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
        max="10485100",
        encoding="base64;jpg",
    ),
    ValueTemplate.IMAGE_PNG: ValueSettinsSchema(
        value_type=ValueBaseType.BLOB,
        type="image",
        max="10485100",
        encoding="base64;png",
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
    ValueTemplate.ALTITUDE_M: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="altitude",
        mapping=None,
        ordered_mapping=None,
        meaningful_zero=None,
        min="-10000",
        max="10000",
        step="0.01",
        unit="m",
        si_conversion=None,
    ),
    ValueTemplate.STREET: ValueSettinsSchema(
        value_type=ValueBaseType.STRING,
        type="street",
        max="85",
        encoding="",
    ),
    ValueTemplate.CITY: ValueSettinsSchema(
        value_type=ValueBaseType.STRING,
        type="city",
        max="85",
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
        max="56",
        encoding="",
    ),
    ValueTemplate.COUNTRY_CODE: ValueSettinsSchema(
        value_type=ValueBaseType.STRING,
        type="country_code",
        max="2",
        encoding="ISO 3166-1 Alpha-2",
    ),
    ValueTemplate.ADDRESS_NAME: ValueSettinsSchema(
        value_type=ValueBaseType.STRING,
        type="address_name",
        max="85",
        encoding="",
    ),
    ValueTemplate.ORGANIZATION: ValueSettinsSchema(
        value_type=ValueBaseType.STRING,
        type="organization",
        max="85",
        encoding="",
    ),
    ValueTemplate.EMAIL: ValueSettinsSchema(
        value_type=ValueBaseType.STRING,
        type="email",
        max="128",
        encoding="",
    ),
    ValueTemplate.PHONE: ValueSettinsSchema(
        value_type=ValueBaseType.STRING,
        type="phone",
        max="32",
        encoding="",
    ),
    ValueTemplate.IDENTIFIER: ValueSettinsSchema(
        value_type=ValueBaseType.STRING,
        type="identifier",
        max="50",
        encoding="",
    ),
    ValueTemplate.JSON: ValueSettinsSchema(
        value_type=ValueBaseType.BLOB,
        type="json",
        max="20000",
        encoding="json",
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
        encoding="",
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
