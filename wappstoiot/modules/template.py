from abc import ABC
from abc import abstractmethod

from typing import Any
from typing import Dict
from typing import Callable
# from typing import Union
# from typing import List
# from typing import TypeVar
from typing import Optional

from enum import Enum

from pydantic import BaseModel
from pydantic import UUID4
# from pydantic import HttpUrl

from ..service.template import ServiceClass

from ..schema.base_schema import WappstoObject

# from ..schema.iot_schema import WappstoObjectType


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


class ValueType(str, Enum):
    """
    Predefined ValueTypes.

    Each of the predefined ValueTypes, have default
    value parameters set, which include BaseType, name,
    permission, range, step and the unit.
    """

    STRING = "String"
    NUMBER = "Number"
    BLOB = "Blob"
    XML = "Xml"
    TEMPERATURE_CELCIUS = "Temperature Celcius"
    BOOLEAN = "Boolean"
    LATITUDE = "Latitude"
    LONGITUDE = "Longitude"
    CO2 = "CO2"
    PRESSURE_PASCAL = "Pressure Pascal"
    HUMIDITY = "Humidity"


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
    unit: Optional[str]


valueSettings: Dict[ValueType, ValueSettinsSchema] = {
    ValueType.STRING: ValueSettinsSchema(
        value_type=ValueBaseType.STRING,
        type="String",
        max=64,
        encoding="utf-8",
    ),
    ValueType.NUMBER: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="Number",
        mapping=None,  # dict,
        ordered_mapping=None,  # Boolean
        meaningful_zero=None,  # Boolean
        min=-1e+38,  # UNSURE(MBK): !!
        max=1e+38,
        step=0.01,
        unit=None
    ),
    ValueType.BLOB: ValueSettinsSchema(
        value_type=ValueBaseType.BLOB,
        type="Blob",
        max=64,
        encoding="base64"
    ),
    ValueType.XML: ValueSettinsSchema(
        value_type=ValueBaseType.XML,
        type="Xml",
        xsd="",
        namespace=""
    ),
    ValueType.TEMPERATURE_CELCIUS: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="temperature",
        mapping=None,  # dict,
        ordered_mapping=None,  # Boolean
        meaningful_zero=False,  # Boolean
        min=-273,
        max=1e+38,
        step=0.01,
        unit="°C",
    ),
    ValueType.CO2: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="co2",
        mapping=None,  # dict,
        ordered_mapping=None,  # Boolean
        meaningful_zero=True,  # Boolean
        min=0,
        max=1e+38,
        step=0.01,
        unit="ppm",
        si_conversion="1000000*[ppm]"
    ),
    ValueType.PRESSURE_PASCAL: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="pressure",
        mapping=None,  # dict,
        ordered_mapping=None,  # Boolean
        meaningful_zero=True,  # Boolean
        min=0,
        max=1e+38,
        step=0.01,
        unit="Pa",
    ),
    ValueType.HUMIDITY: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="humidity",
        mapping=None,  # dict,
        ordered_mapping=None,  # Boolean
        meaningful_zero=True,  # Boolean
        min=0,
        max=1e+38,
        step=0.01,
        unit="%"
    ),
    ValueType.LATITUDE: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="latitude",
        mapping=None,  # dict,
        ordered_mapping=None,  # Boolean
        meaningful_zero=True,  # Boolean
        min=-90,
        max=90,
        step=0.000001,
        unit="°N"
    ),
    ValueType.LONGITUDE: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="longitude",
        mapping=None,  # dict,
        ordered_mapping=None,  # Boolean
        meaningful_zero=True,  # Boolean
        min=-180,
        max=180,
        step=0.000001,
        unit="°E"
    ),
    ValueType.BOOLEAN: ValueSettinsSchema(
        value_type=ValueBaseType.NUMBER,
        type="boolean",
        mapping=None,  # dict,
        ordered_mapping=None,  # Boolean
        meaningful_zero=True,  # Boolean
        min=0,
        max=1,
        step=1,
        unit="Boolean"
    ),
}

# #############################################################################
#                             Config-File Schema
# #############################################################################


# class _UnitsInfo(BaseModel):
#     self_type: WappstoObjectType
#     parent: Optional[UUID4] = None
#     name: Optional[str] = None
#     self_id: int
#     children: List[UUID4]
#     children_id_mapping: Dict[int, UUID4]
#     children_name_mapping: Dict[str, UUID4]


# class _Config(BaseModel):
#     network_uuid: UUID4
#     # network_name: str  # Really needed?
#     port: int
#     end_point: HttpUrl
#     # connectSync: Optional[bool]
#     # storeQueue: Optional[bool]
#     # mixMaxEnforce: Optional[str]
#     # stepEnforce: Optional[str]
#     # deltaHandling: Optional[str]
#     # period_handling: Optional[str]


# class _ConfigFile(BaseModel):
#     configs: _Config
#     # NOTE: the str, should be UUID4, but can't do to pydantic error!
#     units: Dict[str, _UnitsInfo]


def dict_diff(olddict: Dict[Any, Any], newdict: Dict[Any, Any]):
    """Find & return what have updated from old to new dictionary."""
    return dict(set(newdict.items() - set(olddict.items())))


# #############################################################################
#                             Wappsto-Device Template
# #############################################################################

class WappstoUnit(ABC):

    schema: WappstoObject

    @property
    @abstractmethod
    def uuid(self) -> UUID4:
        pass

    # @abstractmethod
    # @property
    # def name(self) -> str:
    #     pass

    @property
    def id(self) -> int:
        pass

    @property
    @abstractmethod
    def children_uuid_mapping(self) -> Dict[UUID4, Callable]:
        pass

    @property
    @abstractmethod
    def children_id_mapping(self) -> Dict[int, UUID4]:
        pass

    @property
    @abstractmethod
    def children_name_mapping(self) -> Dict[str, UUID4]:
        pass

    @property
    @abstractmethod
    def connection(self) -> ServiceClass:
        pass

    # @abstractmethod
    # def _get_json(self) -> List[_UnitsInfo]:
    #     pass

    @abstractmethod
    def delete(self):
        pass

    @abstractmethod
    def change(self):
        pass

    @abstractmethod
    def onChange(self):
        pass

    @abstractmethod
    def onRequest(self):
        pass

    @abstractmethod
    def onRefresh(self):
        pass

    @abstractmethod
    def onDelete(self):
        pass
