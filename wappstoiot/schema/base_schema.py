# generated by datamodel-codegen:
#   filename:  schema.json
#   timestamp: 2021-07-08T11:31:02+00:00

# from __future__ import annotations

from datetime import datetime
from enum import Enum

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from pydantic import BaseModel
from pydantic import conint
from pydantic import constr
from pydantic import Extra
from pydantic import Field
from pydantic import UUID4


def timestamp(dt: datetime) -> str:
    """
    Return The default timestamp used for Wappsto.

    The timestamp are always set to the UTC timezone.

    Returns:
        The UTC time string in ISO format.
    """
    return dt.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')


class WappstoMethods(str, Enum):
    """The methods that the Wappsto are using."""
    DELETE = "DELETE"
    PUT = "PUT"
    POST = "POST"
    GET = "GET"


class InclusionStatus(str, Enum):
    STATUS_DEVICE_INCLUDING = 'STATUS_DEVICE_INCLUDING'
    STATUS_DEVICE_INCLUSION_SUCCESS = 'STATUS_DEVICE_INCLUSION_SUCCESS'
    STATUS_DEVICE_INCLUSION_FAILURE = 'STATUS_DEVICE_INCLUSION_FAILURE'
    STATUS_DEVICE_REPORTING = 'STATUS_DEVICE_REPORTING'
    STATUS_DEVICE_REPORT_SUCCESS = 'STATUS_DEVICE_REPORT_SUCCESS'
    STATUS_DEVICE_REPORT_FAILURE = 'STATUS_DEVICE_REPORT_FAILURE'
    EXCLUDED = 'EXCLUDED'
    INCLUDED = 'INCLUDED'


class FirmwareStatus(str, Enum):
    UP_TO_DATE = 'UP_TO_DATE'
    UPDATE_AVAILABLE = 'UPDATE_AVAILABLE'
    UPLOADING = 'UPLOADING'
    UPLOAD_COMPLETE = 'UPLOAD_COMPLETE'
    UPLOADING_FAILURE = 'UPLOADING_FAILURE'
    FLASHING = 'FLASHING'
    FLASHING_COMPLETE = 'FLASHING_COMPLETE'
    FLASHING_FAILURE = 'FLASHING_FAILURE'


class Command(str, Enum):
    IDLE = 'idle'
    FIRMWARE_UPLOAD = 'firmware_upload'
    FIRMWARE_FLASH = 'firmware_flash'
    FIRMWARE_CANCEL = 'firmware_cancel'
    INCLUDE = 'include'
    EXCLUDE = 'exclude'
    CONNECTION_CHECK = 'connection_check'


class OwnerEnum(str, Enum):
    UNASSIGNED = 'unassigned'


class Deletion(str, Enum):
    PENDING = 'pending'
    FAILED = 'failed'


class WappstoVersion(str, Enum):
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
    OK = 'ok'
    UPDATE = 'update'
    PENDING = 'pending'


class StateType(str, Enum):
    REPORT = 'Report'
    CONTROL = 'Control'


class StateStatus(str, Enum):
    SEND = 'Send'
    PENDING = 'Pending'
    FAILED = 'Failed'


class Level(str, Enum):
    IMPORTANT = 'important'
    ERROR = 'error'
    WARNING = 'warning'
    INFO = 'info'
    DEBUG = 'debug'


class StatusType(str, Enum):
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


class Connection(BaseModel):
    timestamp: Optional[datetime] = None
    online: Optional[bool] = None

    class Config:
        json_encoders = {
            datetime: timestamp
        }


class WarningItem(BaseModel):
    message: Optional[Optional[str]] = None
    data: Optional[Optional[Dict[str, Any]]] = None
    code: Optional[Optional[int]] = None


class Geo(BaseModel):
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    display_name: Optional[str] = None
    address: Optional[Dict[str, Any]] = None


class BaseMeta(BaseModel):  # Base Meta
    id: Optional[UUID4] = None
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
    redirect: Optional[  # type: ignore
        constr(regex=r'^[0-9a-zA-Z_-]+$', min_length=1, max_length=200)
    ] = None
    
    error: Optional[UUID4] = None
    warning: Optional[List[WarningItem]] = None
    trace: Optional[Optional[str]] = None

    set: Optional[List[UUID4]] = None
    contract: Optional[List[UUID4]] = None

    class Config:
        json_encoders = {
            datetime: timestamp
        }


class StatusMeta(BaseMeta):
    class WappstoMetaType(str, Enum):
        STATUS = "status"
    type: Optional[WappstoMetaType] = None


class ValueMeta(BaseMeta):
    class WappstoMetaType(str, Enum):
        VALUE = "value"
    type: Optional[WappstoMetaType] = None

    historical: Optional[bool] = None 


class StateMeta(BaseMeta):
    class WappstoMetaType(str, Enum):
        STATE = "state"
    type: Optional[WappstoMetaType] = None

    historical: Optional[bool] = None 


class DeviceMeta(BaseMeta):
    class WappstoMetaType(str, Enum):
        DEVICE = "device"
    type: Optional[WappstoMetaType] = None

    geo: Optional[Geo] = None
    historical: Optional[bool] = None


class NetworkMeta(BaseMeta):
    class WappstoMetaType(str, Enum):
        NETWORK = "network"
    type: Optional[WappstoMetaType] = None

    geo: Optional[Geo] = None
    historical: Optional[bool] = None

    connection: Optional[Connection] = None
    accept_test_mode: Optional[bool] = None
    verify_product: Optional[str] = None
    product: Optional[str] = None


class Status(BaseModel):
    message: str
    timestamp: datetime
    data: Optional[str] = None
    level: Level
    type: Optional[StatusType]
    meta: Optional[StatusMeta] = Field(None, title='meta-2.0:create')

    class Config:
        json_encoders = {
            datetime: timestamp
        }


class Info(BaseModel):
    enabled: Optional[bool] = None


class State(BaseModel):
    data: str
    type: Optional[StateType]

    meta: Optional[StateMeta] = Field(None, title='meta-2.0:create')
    status: Optional[StateStatus] = None
    status_payment: Optional[str] = None
    timestamp: Optional[datetime] = None

    class Config:
        extra = Extra.forbid
        json_encoders = {
            datetime: timestamp,
        }


class BaseValue(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None

    description: Optional[str] = None
    period: Optional[str] = None
    delta: Optional[str] = None
    permission: Optional[PermissionType] = None
    status: Optional[EventStatus] = None
    meta: Optional[ValueMeta] = Field(None, title='meta-2.0:create')
    state: Optional[List[Union[State, UUID4]]] = None
    info: Optional[Info] = None

    class Config:
        extra = Extra.forbid


class Number(BaseModel):
    min: float
    max: float
    step: float
    mapping: Optional[Dict[str, Any]] = None
    meaningful_zero: Optional[bool] = None
    ordered_mapping: Optional[bool] = None
    si_conversion: Optional[str] = None
    unit: Optional[str] = None

    class Config:
        extra = Extra.forbid


class String(BaseModel):
    max: Optional[conint(ge=1, multiple_of=1)] = None  # type: ignore
    encoding: Optional[str] = None


class Blob(BaseModel):
    max: Optional[conint(ge=1, multiple_of=1)] = None  # type: ignore
    encoding: Optional[str] = None


class Xml(BaseModel):
    xsd: Optional[str] = None
    namespace: Optional[str] = None


class StringValue(BaseValue):
    string: Optional[String] = None

    class Config:
        extra = Extra.forbid


class NumberValue(BaseValue):
    number: Optional[Number] = None

    class Config:
        extra = Extra.forbid


class BlobValue(BaseValue):
    blob: Optional[Blob] = None

    class Config:
        extra = Extra.forbid


class XmlValue(BaseValue):
    xml: Optional[Xml] = None

    class Config:
        extra = Extra.forbid


class Device(BaseModel):
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

    class Config:
        extra = Extra.forbid


class Network(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    device: Optional[List[Union[Device, UUID4]]] = None
    meta: Optional[NetworkMeta] = Field(None, title='meta-2.0:create')
    info: Optional[Info] = None

    class Config:
        extra = Extra.forbid


WappstoObject = Union[
    Network,
    Device,
    StringValue,
    NumberValue,
    BlobValue,
    XmlValue,
    State
]