"""Contain the basic Wappsto schema for the network structure and children."""
from datetime import datetime
from enum import Enum

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
# from typing import TypeAlias
from typing import Union

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import conint
# from pydantic import constr
from pydantic import Field
from pydantic import field_serializer
from pydantic import GenerateSchema
from pydantic import UUID4

from pydantic_core import CoreSchema
from pydantic_core import core_schema


class LaxStrGenerator(GenerateSchema):
    """
    A more relax converter, that make it work like Pydantic v1.

    URL: https://github.com/pydantic/pydantic/issues/6045#issuecomment-1650443311
    """

    def str_schema(self) -> CoreSchema:
        """Convert a string more relaxed."""
        return core_schema.no_info_before_validator_function(str, core_schema.str_schema())


BaseModel.model_config = ConfigDict(schema_generator=LaxStrGenerator)


def timestamp_converter(dt: datetime) -> Optional[str]:
    """
    Return The default timestamp used for Wappsto.

    The timestamp are always set to the UTC timezone.

    Returns:
        The UTC time string in ISO format.
    """
    if dt is None:
        return None
    return dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')


class WappstoMethods(str, Enum):
    """The methods that the Wappsto are using."""

    DELETE = "DELETE"
    PUT = "PUT"
    POST = "POST"
    GET = "GET"


class InclusionStatus(str, Enum):
    """The possible inclusion status for a device."""

    STATUS_DEVICE_INCLUDING = 'STATUS_DEVICE_INCLUDING'
    STATUS_DEVICE_INCLUSION_SUCCESS = 'STATUS_DEVICE_INCLUSION_SUCCESS'
    STATUS_DEVICE_INCLUSION_FAILURE = 'STATUS_DEVICE_INCLUSION_FAILURE'
    STATUS_DEVICE_REPORTING = 'STATUS_DEVICE_REPORTING'
    STATUS_DEVICE_REPORT_SUCCESS = 'STATUS_DEVICE_REPORT_SUCCESS'
    STATUS_DEVICE_REPORT_FAILURE = 'STATUS_DEVICE_REPORT_FAILURE'
    EXCLUDED = 'EXCLUDED'
    INCLUDED = 'INCLUDED'


class FirmwareStatus(str, Enum):
    """The possible firmware status for a device."""

    UP_TO_DATE = 'UP_TO_DATE'
    UPDATE_AVAILABLE = 'UPDATE_AVAILABLE'
    UPLOADING = 'UPLOADING'
    UPLOAD_COMPLETE = 'UPLOAD_COMPLETE'
    UPLOADING_FAILURE = 'UPLOADING_FAILURE'
    FLASHING = 'FLASHING'
    FLASHING_COMPLETE = 'FLASHING_COMPLETE'
    FLASHING_FAILURE = 'FLASHING_FAILURE'


class Command(str, Enum):
    """The possible firmware status for a device."""

    IDLE = 'idle'
    FIRMWARE_UPLOAD = 'firmware_upload'
    FIRMWARE_FLASH = 'firmware_flash'
    FIRMWARE_CANCEL = 'firmware_cancel'
    INCLUDE = 'include'
    EXCLUDE = 'exclude'
    CONNECTION_CHECK = 'connection_check'


class OwnerEnum(str, Enum):
    """The Owner of the Object."""

    UNASSIGNED = 'unassigned'


class Deletion(str, Enum):
    """The Status of a deletion request."""

    PENDING = 'pending'
    FAILED = 'failed'


class WappstoVersion(str, Enum):
    """The different version available."""

    V2_0 = "2.0"
    V2_1 = "2.1"


class PermissionType(str, Enum):
    """All possible Value Permission Types."""

    READ = 'r'
    WRITE = 'w'
    READWRITE = 'rw'
    WRITEREAD = 'wr'
    NONE = 'none'


class EventStatus(str, Enum):
    """Update status/request."""

    OK = 'ok'
    UPDATE = 'update'
    PENDING = 'pending'


class StateType(str, Enum):
    """All the State type."""

    REPORT = 'Report'
    CONTROL = 'Control'


class StateStatus(str, Enum):
    """Update status/request."""

    SEND = 'Send'
    PENDING = 'Pending'
    FAILED = 'Failed'


class Level(str, Enum):
    """The different log levels."""

    IMPORTANT = 'important'
    ERROR = 'error'
    WARNING = 'warning'
    SUCCESS = 'success'
    INFO = 'info'
    DEBUG = 'debug'


class StatusType(str, Enum):
    """The different status types."""

    PUBLIC_KEY = 'public key'
    MEMORY_INFORMATION = 'memory information'
    DEVICE_DESCRIPTION = 'device description'
    VALUE_DESCRIPTION = 'value description'
    VALUE = 'value'
    PARTNER_INFORMATION = 'partner information'
    ACTION = 'action'
    CALCULATION = 'calculation'
    TIMER = 'timer'
    CALENDAR = 'calendar'
    STATEMACHINE = 'statemachine'
    FIRMWARE_UPDATE = 'firmware update'
    CONFIGURATION = 'configuration'
    EXI = 'exi'
    SYSTEM = 'system'
    APPLICATION = 'application'
    GATEWAY = 'gateway'


class WappstoMetaType(str, Enum):
    """
    All possible Wappsto Meta Types.

    They have a parent child relation in order of:
    network->device->value->state

    Where a 'Network' only contains 'Device's,
    'Device's only contains 'value's, and
    'Value's only contains 'State's.
    """

    NETWORK = "network"
    DEVICE = "device"
    VALUE = "value"
    STATE = "state"
    CREATOR = "creator"
    IDLIST = "idlist"
    DELETELIST = "deletelist"


class Connection(BaseModel):
    """The Connection info for the network."""

    timestamp: Optional[datetime] = None
    online: Optional[bool] = None

    @field_serializer('timestamp')
    def serialize_timestamp(self, value: datetime) -> Optional[str]:
        """Convert datetime to Wappsto datetime standard."""
        return timestamp_converter(value)


class WarningItem(BaseModel):
    """The Connection info for the network."""

    message: Optional[Optional[str]] = None
    data: Optional[Optional[Dict[str, Any]]] = None
    code: Optional[Optional[int]] = None


class Geo(BaseModel):
    """The geolocation structure for network & device objects."""

    latitude: Optional[str] = None
    longitude: Optional[str] = None
    display_name: Optional[str] = None
    address: Optional[Dict[str, Any]] = None


class BaseMeta(BaseModel):
    """The base for all meta objects."""

    id: Optional[UUID4] = None
    # NOTE: Set in the children-class to enforce right BaseModel type.
    # #  type: Optional[WappstoMetaType] = None
    version: Optional[WappstoVersion] = None

    manufacturer: Optional[UUID4] = None
    owner: Optional[Union[UUID4, OwnerEnum]] = None
    parent: Optional[UUID4] = None

    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    changed: Optional[datetime] = None

    application: Optional[UUID4] = None
    deletion: Optional[Deletion] = None
    deprecated: Optional[Optional[bool]] = None

    iot: Optional[Optional[bool]] = None
    revision: Optional[Optional[int]] = None
    size: Optional[Optional[int]] = None
    path: Optional[Optional[str]] = None

    oem: Optional[Optional[str]] = None
    accept_manufacturer_as_owner: Optional[Optional[bool]] = None

    # NOTE: patterns do not work while the `LaxStrGenerator` are in use.
    # redirect: Optional[  # type: ignore
    #     constr(
    #         pattern=r'^[0-9a-zA-Z_-]+$',  # noqa: F722
    #         min_length=1,
    #         max_length=200
    #     )
    # ] = None

    error: Optional[UUID4] = None
    warning: Optional[List[WarningItem]] = None
    trace: Optional[Optional[str]] = None

    set: Optional[List[UUID4]] = None
    contract: Optional[List[UUID4]] = None

    historical: Optional[bool] = None

    @field_serializer('created', 'updated', 'changed')
    def serialize_timestamp(self, value: datetime) -> Optional[str]:
        """Convert datetime to Wappsto datetime standard."""
        return timestamp_converter(value)


class EventlogMeta(BaseMeta):
    """The meta object for the Eventlog structure."""

    class WappstoMetaType(str, Enum):
        """Used instead of typing.Literal."""

        STATUS = "eventlog"

    type: Optional[WappstoMetaType] = None

    icon: Optional[Optional[str]] = None
    alert: Optional[List[UUID4]] = None


class StatusMeta(BaseMeta):
    """The meta object for the Status structure."""

    class WappstoMetaType(str, Enum):
        """Used instead of typing.Literal."""

        STATUS = "status"
    type: Optional[WappstoMetaType] = None

    icon: Optional[Optional[str]] = None
    alert: Optional[List[UUID4]] = None


class ValueMeta(BaseMeta):
    """The meta object for the Value structure."""

    class WappstoMetaType(str, Enum):
        """Used instead of typing.Literal."""

        VALUE = "value"
    type: Optional[WappstoMetaType] = None


class StateMeta(BaseMeta):
    """The meta object for the State structure."""

    class WappstoMetaType(str, Enum):
        """Used instead of typing.Literal."""

        STATE = "state"
    type: Optional[WappstoMetaType] = None


class DeviceMeta(BaseMeta):
    """The meta object for the Device structure."""

    class WappstoMetaType(str, Enum):
        """Used instead of typing.Literal."""

        DEVICE = "device"

    type: Optional[WappstoMetaType] = None

    geo: Optional[Geo] = None


class NetworkMeta(BaseMeta):
    """The meta object for the Network structure."""

    class WappstoMetaType(str, Enum):
        """Used instead of typing.Literal."""

        NETWORK = "network"

    type: Optional[WappstoMetaType] = None

    geo: Optional[Geo] = None
    connection: Optional[Connection] = None
    accept_test_mode: Optional[bool] = None
    verify_product: Optional[str] = None
    product: Optional[str] = None


class Status(BaseModel):
    """Contain the status."""

    message: str
    timestamp: datetime
    data: Optional[str] = None
    level: Level
    type: Optional[StatusType]
    meta: Optional[StatusMeta] = Field(None, title='meta-2.0:create')

    @field_serializer('timestamp')
    def serialize_timestamp(self, value: datetime) -> Optional[str]:
        """Convert datetime to Wappsto datetime standard."""
        return timestamp_converter(value)


class Info(BaseModel):
    """."""

    enabled: Optional[bool] = None


class LogValue(BaseModel):
    """The required data for post of new values."""

    data: str
    timestamp: datetime

    model_config: ConfigDict = ConfigDict(extra='forbid')  # type: ignore

    @field_serializer('timestamp')
    def serialize_timestamp(self, value: datetime) -> Optional[str]:
        """Convert datetime to Wappsto datetime standard."""
        return timestamp_converter(value)


class State(BaseModel):
    """The State object found in values, that contain the raw value."""

    data: str
    type: Optional[StateType] = None

    meta: Optional[StateMeta] = Field(None, title='meta-2.0:create')
    status: Optional[StateStatus] = None
    status_payment: Optional[str] = None
    timestamp: Optional[datetime] = None

    model_config: ConfigDict = ConfigDict(extra='forbid')  # type: ignore

    @field_serializer('timestamp')
    def serialize_timestamp(self, value: datetime) -> Optional[str]:
        """Convert datetime to Wappsto datetime standard."""
        return timestamp_converter(value)


class EventlogItem(BaseModel):
    """Event Log structure, found in values.."""

    message: str
    timestamp: Optional[datetime] = None
    info: Optional[Dict[str, Any]] = None
    level: Level
    type: Optional[str] = None
    meta: Optional[EventlogMeta] = Field(None, title='meta-2.0:create')

    @field_serializer('timestamp')
    def serialize_timestamp(self, value: datetime) -> Optional[str]:
        """Convert datetime to Wappsto datetime standard."""
        return timestamp_converter(value)


class BaseValue(BaseModel):
    """Base structure for all values types, what all values have."""

    name: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    period: Optional[str] = None
    delta: Optional[str] = None
    permission: Optional[PermissionType] = None
    status: Optional[EventStatus] = None
    meta: Optional[ValueMeta] = Field(None, title='meta-2.0:create')
    state: Optional[List[Union[State, UUID4]]] = None
    eventlog: Optional[List[Union[EventlogItem, UUID4]]] = None
    info: Optional[Info] = None

    model_config: ConfigDict = ConfigDict(extra='forbid')  # type: ignore


class Number(BaseModel):
    """Substructure for the Number value."""

    min: Union[float, int, str]
    max: Union[float, int, str]
    step: Union[float, int, str]
    mapping: Optional[Dict[str, Any]] = None
    meaningful_zero: Optional[bool] = None
    ordered_mapping: Optional[bool] = None
    si_conversion: Optional[str] = None
    unit: Optional[str] = None


class String(BaseModel):
    """Substructure for the String value."""

    max: Optional[conint(ge=1, multiple_of=1)] = None  # type: ignore
    encoding: Optional[str] = None


class Blob(BaseModel):
    """Substructure for the Blob value."""

    max: Optional[conint(ge=1, multiple_of=1)] = None  # type: ignore
    encoding: Optional[str] = None


class Xml(BaseModel):
    """Substructure for the XML value."""

    xsd: Optional[str] = None
    namespace: Optional[str] = None


class StringValue(BaseValue):
    """One of four Value type."""

    string: Optional[String] = None

    model_config: ConfigDict = ConfigDict(extra='forbid')  # type: ignore

    # @model_validator(mode='before')
    # def value_type_check(cls, values: Dict[str, Any]):
    #     """Force the Validate for the value type."""
    #     keys = ["number", "blob", "xml"]
    #     if any(key in values for key in keys):
    #         raise TypeError(f"A Wappsto string value can not contain: {' '.join(keys)}")
    #     return values


class NumberValue(BaseValue):
    """One of four Value type."""

    number: Optional[Number] = None

    model_config: ConfigDict = ConfigDict(extra='forbid')  # type: ignore

    # @model_validator(mode='before')
    # def value_type_check(cls, values: Dict[str, Any]):
    #     """Force the Validate for the value type."""
    #     keys = ["string", "blob", "xml"]
    #     if any(key in values for key in keys):
    #         raise TypeError(f"A Wappsto number value can not contain: {' '.join(keys)}")
    #     return values


class BlobValue(BaseValue):
    """One of four Value type."""

    blob: Optional[Blob] = None

    model_config: ConfigDict = ConfigDict(extra='forbid')  # type: ignore

    # @model_validator(mode='before')
    # def value_type_check(cls, values: Dict[str, Any]):
    #     """Force the Validate for the value type."""
    #     keys = ["number", "string", "xml"]
    #     if any(key in values for key in keys):
    #         raise TypeError(f"A Wappsto blob value can not contain: {' '.join(keys)}")
    #     return values


class XmlValue(BaseValue):
    """One of four Value type."""

    xml: Optional[Xml] = None

    model_config: ConfigDict = ConfigDict(extra='forbid')  # type: ignore

    # @model_validator(mode='before')
    # def value_type_check(cls, values: Dict[str, Any]):
    #     """Force the Validate for the value type."""
    #     keys = ["number", "blob", "string"]
    #     if any(key in values for key in keys):
    #         raise TypeError(f"A Wappsto xml value can not contain: {' '.join(keys)}")
    #     return values


class Device(BaseModel):
    """The Wappsto device structure."""

    name: Optional[str] = None
    control_timeout: Optional[int] = None
    control_when_offline: Optional[bool] = None
    manufacturer: Optional[str] = None
    product: Optional[str] = None
    version: Optional[str] = None
    serial: Optional[str] = None
    description: Optional[str] = None
    protocol: Optional[str] = None
    communication: Optional[str] = None
    included: Optional[str] = None
    inclusion_status: Optional[InclusionStatus] = None
    firmware_status: Optional[FirmwareStatus] = None
    firmware_upload_progress: Optional[str] = None
    firmware_available_version: Optional[str] = None
    command: Optional[Command] = None
    meta: Optional[DeviceMeta] = Field(None, title='meta-2.0:create')
    status: Optional[List[Union[Status, UUID4]]] = None
    value: Optional[
        List[
            Union[
                StringValue,
                NumberValue,
                BlobValue,
                XmlValue,
                UUID4
            ]
        ]
    ] = None
    info: Optional[Info] = None

    # model_config: ConfigDict = ConfigDict(extra='forbid')  # type: ignore


class Network(BaseModel):
    """The root wappsto structure, for all IoT data."""

    name: Optional[str] = None
    description: Optional[str] = None
    device: Optional[List[Union[Device, UUID4]]] = None
    meta: Optional[NetworkMeta] = Field(None, title='meta-2.0:create')
    info: Optional[Info] = None

    # model_config: ConfigDict = ConfigDict(extra='forbid')  # type: ignore


class ApiMetaTypes(str, Enum):
    """The enum list of the different list types."""

    idlist = "idlist"
    deletelist = "deletelist"


class ApiMetaInfo(BaseModel):
    """The meta structure for list types."""

    type: ApiMetaTypes  # Merge with MetaAPIData?
    version: WappstoVersion


class childInfo(BaseModel):
    """The info of the returned object in the Id List."""

    type: WappstoMetaType
    version: WappstoVersion


class IdList(BaseModel):
    """The structure reply when a list of objects have been requested."""

    child: List[childInfo]
    id: List[UUID4]
    more: bool
    limit: int
    count: int
    meta: ApiMetaInfo

    model_config: ConfigDict = ConfigDict(extra='forbid')  # type: ignore


class DeleteList(BaseModel):
    """The structure reply when a delete request and been send."""

    deleted: List[UUID4]
    code: int
    message: str = "Deleted"
    meta: ApiMetaInfo


"""A collection of all Wappsto Value Types."""
Value = Union[StringValue, NumberValue, BlobValue, XmlValue]
ValueUnion = Union[StringValue, NumberValue, BlobValue, XmlValue]

"""A collection of all Wappsto Types."""
WappstoObject = Union[Network, Device, Value, State, IdList, DeleteList]
