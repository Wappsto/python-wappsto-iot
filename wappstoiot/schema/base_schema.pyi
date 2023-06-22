from _typeshed import Incomplete
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, UUID4 as UUID4, conint as conint, constr as constr
from typing import Any, Dict, List, Optional, Union

def timestamp_converter(dt: datetime) -> str: ...

class WappstoMethods(str, Enum):
    DELETE: str
    PUT: str
    POST: str
    GET: str

class InclusionStatus(str, Enum):
    STATUS_DEVICE_INCLUDING: str
    STATUS_DEVICE_INCLUSION_SUCCESS: str
    STATUS_DEVICE_INCLUSION_FAILURE: str
    STATUS_DEVICE_REPORTING: str
    STATUS_DEVICE_REPORT_SUCCESS: str
    STATUS_DEVICE_REPORT_FAILURE: str
    EXCLUDED: str
    INCLUDED: str

class FirmwareStatus(str, Enum):
    UP_TO_DATE: str
    UPDATE_AVAILABLE: str
    UPLOADING: str
    UPLOAD_COMPLETE: str
    UPLOADING_FAILURE: str
    FLASHING: str
    FLASHING_COMPLETE: str
    FLASHING_FAILURE: str

class Command(str, Enum):
    IDLE: str
    FIRMWARE_UPLOAD: str
    FIRMWARE_FLASH: str
    FIRMWARE_CANCEL: str
    INCLUDE: str
    EXCLUDE: str
    CONNECTION_CHECK: str

class OwnerEnum(str, Enum):
    UNASSIGNED: str

class Deletion(str, Enum):
    PENDING: str
    FAILED: str

class WappstoVersion(str, Enum):
    V2_0: str
    V2_1: str

class PermissionType(str, Enum):
    READ: str
    WRITE: str
    READWRITE: str
    WRITEREAD: str
    NONE: str

class EventStatus(str, Enum):
    OK: str
    UPDATE: str
    PENDING: str

class StateType(str, Enum):
    REPORT: str
    CONTROL: str

class StateStatus(str, Enum):
    SEND: str
    PENDING: str
    FAILED: str

class Level(str, Enum):
    IMPORTANT: str
    ERROR: str
    WARNING: str
    SUCCESS: str
    INFO: str
    DEBUG: str

class StatusType(str, Enum):
    PUBLIC_KEY: str
    MEMORY_INFORMATION: str
    DEVICE_DESCRIPTION: str
    VALUE_DESCRIPTION: str
    VALUE: str
    PARTNER_INFORMATION: str
    ACTION: str
    CALCULATION: str
    TIMER: str
    CALENDAR: str
    STATEMACHINE: str
    FIRMWARE_UPDATE: str
    CONFIGURATION: str
    EXI: str
    SYSTEM: str
    APPLICATION: str
    GATEWAY: str

class WappstoMetaType(str, Enum):
    NETWORK: str
    DEVICE: str
    VALUE: str
    STATE: str
    CREATOR: str
    IDLIST: str
    DELETELIST: str

class Connection(BaseModel):
    timestamp: Optional[datetime]
    online: Optional[bool]
    class Config:
        json_encoders: Incomplete

class WarningItem(BaseModel):
    message: Optional[Optional[str]]
    data: Optional[Optional[Dict[str, Any]]]
    code: Optional[Optional[int]]

class Geo(BaseModel):
    latitude: Optional[str]
    longitude: Optional[str]
    display_name: Optional[str]
    address: Optional[Dict[str, Any]]

class BaseMeta(BaseModel):
    id: Optional[UUID4]
    version: Optional[WappstoVersion]
    manufacturer: Optional[UUID4]
    owner: Optional[Union[UUID4, OwnerEnum]]
    parent: Optional[UUID4]
    created: Optional[datetime]
    updated: Optional[datetime]
    changed: Optional[datetime]
    application: Optional[UUID4]
    deletion: Optional[Deletion]
    deprecated: Optional[Optional[bool]]
    iot: Optional[Optional[bool]]
    revision: Optional[Optional[int]]
    size: Optional[Optional[int]]
    path: Optional[Optional[str]]
    oem: Optional[Optional[str]]
    accept_manufacturer_as_owner: Optional[Optional[bool]]
    redirect: Optional[None]
    error: Optional[UUID4]
    warning: Optional[List[WarningItem]]
    trace: Optional[Optional[str]]
    set: Optional[List[UUID4]]
    contract: Optional[List[UUID4]]
    historical: Optional[bool]
    class Config:
        json_encoders: Incomplete

class EventlogMeta(BaseMeta):
    class WappstoMetaType(str, Enum):
        STATUS: str
    type: Optional[WappstoMetaType]
    icon: Optional[Optional[str]]
    alert: Optional[List[UUID4]]

class StatusMeta(BaseMeta):
    class WappstoMetaType(str, Enum):
        STATUS: str
    type: Optional[WappstoMetaType]
    icon: Optional[Optional[str]]
    alert: Optional[List[UUID4]]

class ValueMeta(BaseMeta):
    class WappstoMetaType(str, Enum):
        VALUE: str
    type: Optional[WappstoMetaType]

class StateMeta(BaseMeta):
    class WappstoMetaType(str, Enum):
        STATE: str
    type: Optional[WappstoMetaType]

class DeviceMeta(BaseMeta):
    class WappstoMetaType(str, Enum):
        DEVICE: str
    type: Optional[WappstoMetaType]
    geo: Optional[Geo]

class NetworkMeta(BaseMeta):
    class WappstoMetaType(str, Enum):
        NETWORK: str
    type: Optional[WappstoMetaType]
    geo: Optional[Geo]
    connection: Optional[Connection]
    accept_test_mode: Optional[bool]
    verify_product: Optional[str]
    product: Optional[str]

class Status(BaseModel):
    message: str
    timestamp: datetime
    data: Optional[str]
    level: Level
    type: Optional[StatusType]
    meta: Optional[StatusMeta]
    class Config:
        json_encoders: Incomplete

class Info(BaseModel):
    enabled: Optional[bool]

class State(BaseModel):
    data: str
    type: Optional[StateType]
    meta: Optional[StateMeta]
    status: Optional[StateStatus]
    status_payment: Optional[str]
    timestamp: Optional[str]
    class Config:
        extra: Incomplete
        json_encoders: Incomplete

class EventlogItem(BaseModel):
    message: str
    timestamp: Optional[datetime]
    info: Optional[Dict[str, Any]]
    level: Level
    type: Optional[str]
    meta: Optional[EventlogMeta]

class BaseValue(BaseModel):
    name: Optional[str]
    type: Optional[str]
    description: Optional[str]
    period: Optional[str]
    delta: Optional[str]
    permission: Optional[PermissionType]
    status: Optional[EventStatus]
    meta: Optional[ValueMeta]
    state: Optional[List[Union[State, UUID4]]]
    eventlog: Optional[List[Union['EventlogItem', UUID4]]]
    info: Optional[Info]

class Number(BaseModel):
    min: float
    max: float
    step: float
    mapping: Optional[Dict[str, Any]]
    meaningful_zero: Optional[bool]
    ordered_mapping: Optional[bool]
    si_conversion: Optional[str]
    unit: Optional[str]

class String(BaseModel):
    max: Optional[None]
    encoding: Optional[str]

class Blob(BaseModel):
    max: Optional[None]
    encoding: Optional[str]

class Xml(BaseModel):
    xsd: Optional[str]
    namespace: Optional[str]

class StringValue(BaseValue):
    string: Optional[String]
    def value_type_check(cls, values): ...

class NumberValue(BaseValue):
    number: Optional[Number]
    def value_type_check(cls, values): ...

class BlobValue(BaseValue):
    blob: Optional[Blob]
    def value_type_check(cls, values): ...

class XmlValue(BaseValue):
    xml: Optional[Xml]
    def value_type_check(cls, values): ...

class Device(BaseModel):
    name: Optional[str]
    control_timeout: Optional[int]
    control_when_offline: Optional[bool]
    manufacturer: Optional[str]
    product: Optional[str]
    version: Optional[str]
    serial: Optional[str]
    description: Optional[str]
    protocol: Optional[str]
    communication: Optional[str]
    included: Optional[str]
    inclusion_status: Optional[InclusionStatus]
    firmware_status: Optional[FirmwareStatus]
    firmware_upload_progress: Optional[str]
    firmware_available_version: Optional[str]
    command: Optional[Command]
    meta: Optional[DeviceMeta]
    status: Optional[List[Union[Status, UUID4]]]
    value: Optional[List[Union[StringValue, NumberValue, BlobValue, XmlValue, UUID4]]]
    info: Optional[Info]

class Network(BaseModel):
    name: Optional[str]
    description: Optional[str]
    device: Optional[List[Union[Device, UUID4]]]
    meta: Optional[NetworkMeta]
    info: Optional[Info]

class ApiMetaTypes(str, Enum):
    idlist: str
    deletelist: str

class ApiMetaInfo(BaseModel):
    type: ApiMetaTypes
    version: WappstoVersion

class childInfo(BaseModel):
    type: WappstoMetaType
    version: WappstoVersion

class IdList(BaseModel):
    child: List[childInfo]
    id: List[UUID4]
    more: bool
    limit: int
    count: int
    meta: ApiMetaInfo
    class Config:
        extra: Incomplete

class DeleteList(BaseModel):
    deleted: List[UUID4]
    code: int
    message: str
    meta: ApiMetaInfo
WappstoObject = Union[Network, Device, StringValue, NumberValue, BlobValue, XmlValue, State, IdList, DeleteList]
