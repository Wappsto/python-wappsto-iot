import uuid
from ..schema.base_schema import PermissionType as PermissionType, timestamp_converter as timestamp_converter
from ..schema.iot_schema import WappstoMethod as WappstoMethod
from ..service.template import ServiceClass as ServiceClass
from ..utils.Timestamp import str_to_datetime as str_to_datetime
from .device import Device as Device
from .template import ValueBaseType as ValueBaseType
from _typeshed import Incomplete
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional, Union

class Period(str, Enum):
    PERIODIC_REFRESH: str
    DROP_UNTIL: str

class Delta(str, Enum):
    ONLY_UPDATE_IF: str
    EXTRA_UPDATES: str

class Value:
    class RequestType(str, Enum):
        refresh: str
        control: str
        delete: str
    class ChangeType(str, Enum):
        report: str
        delta: str
        period: str
        name: str
        description: str
        unit: str
        min: str
        max: str
        step: str
        encoding: str
        meaningful_zero: str
        state: str
    log: Incomplete
    value_type: Incomplete
    schema: Incomplete
    report_state: Incomplete
    control_state: Incomplete
    parent: Incomplete
    element: Incomplete
    children_name_mapping: Incomplete
    connection: Incomplete
    def __init__(self, parent: Device, value_type: ValueBaseType, name: str, value_uuid: Optional[uuid.UUID], type: Optional[str] = ..., permission: PermissionType = ..., min: Optional[Union[int, float]] = ..., max: Optional[Union[int, float]] = ..., step: Optional[Union[int, float]] = ..., encoding: Optional[str] = ..., xsd: Optional[str] = ..., namespace: Optional[str] = ..., period: Optional[int] = ..., delta: Optional[Union[int, float]] = ..., description: Optional[str] = ..., meaningful_zero: Optional[str] = ..., mapping: Optional[bool] = ..., ordered_mapping: Optional[bool] = ..., si_conversion: Optional[str] = ..., unit: Optional[str] = ...) -> None: ...
    def getControlData(self) -> Optional[Union[float, str]]: ...
    def getControlTimestamp(self) -> Optional[datetime]: ...
    def getReportData(self) -> Optional[Union[float, str]]: ...
    def getReportTimestamp(self) -> Optional[datetime]: ...
    @property
    def name(self) -> str: ...
    @property
    def uuid(self) -> uuid.UUID: ...
    def onChange(self, callback: Callable[[Value], None]) -> Callable[[Value], None]: ...
    def cancelOnChange(self) -> None: ...
    def onReport(self, callback: Callable[[Value, Union[str, float]], None]) -> Callable[[Value, Union[str, float]], None]: ...
    def cancelOnReport(self) -> None: ...
    def onControl(self, callback: Callable[[Value, Union[str, float]], None]) -> Callable[[Value, Union[str, float]], None]: ...
    def cancelOnControl(self) -> None: ...
    def onCreate(self, callback: Callable[[Value], None]) -> Callable[[Value], None]: ...
    def cancelOnCreate(self) -> None: ...
    def onRefresh(self, callback: Callable[[Value], None]) -> Callable[[Value], None]: ...
    def cancelOnRefresh(self) -> None: ...
    def onDelete(self, callback: Callable[[Value], None]) -> Callable[[Value], None]: ...
    def cancelOnDelete(self) -> None: ...
    def refresh(self) -> None: ...
    def change(self, name: str, value: Any) -> None: ...
    def delete(self) -> None: ...
    def report(self, value: Union[int, float, str, None], timestamp: Optional[datetime] = ...) -> None: ...
    def control(self, value: Union[int, float, str, None], timestamp: Optional[datetime] = ...) -> None: ...
    def close(self) -> None: ...