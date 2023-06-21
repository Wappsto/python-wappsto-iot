import datetime
import uuid
from .base_schema import BlobValue as BlobValue, DeleteList as DeleteList, Device as Device, IdList as IdList, Network as Network, NumberValue as NumberValue, State as State, StringValue as StringValue, XmlValue as XmlValue
from _typeshed import Incomplete
from enum import Enum
from pydantic import BaseModel
from typing import Any, Dict, List, Optional, Tuple, Union

def parwise(values): ...
ValueUnion = Union[StringValue, NumberValue, BlobValue, XmlValue]
JsonRpc_error_codes: Incomplete

class WappstoObjectType(str, Enum):
    NETWORK: str
    DEVICE: str
    VALUE: str
    STATE: str

ObjectType2BaseModel: Dict[WappstoObjectType, Any]

def url_parser(url: str) -> List[Tuple[WappstoObjectType, Optional[uuid.UUID]]]: ...

class WappstoMethod(str, Enum):
    GET: str
    POST: str
    PATCH: str
    PUT: str
    DELETE: str
    HEAD: str

class Success(BaseModel):
    success: bool
    class Config:
        extra: Incomplete

class Identifier(BaseModel):
    identifier: Optional[str]
    fast: Optional[bool]

class JsonMeta(BaseModel):
    server_send_time: datetime.datetime

class JsonReply(BaseModel):
    value: Optional[Union[Device, Network, State, ValueUnion, IdList, DeleteList, bool]]
    meta: JsonMeta
    class Config:
        extra: Incomplete

class JsonData(BaseModel):
    url: str
    data: Optional[Any]
    meta: Optional[Identifier]
    class Config:
        extra: Incomplete
    def path_check(cls, v, values, **kwargs): ...
    def url_data_mapper(cls, v, values, **kwargs) -> Optional[Union[Network, Device, ValueUnion, State, IdList, DeleteList]]: ...
