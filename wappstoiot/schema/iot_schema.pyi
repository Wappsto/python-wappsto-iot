import datetime
import uuid
from .base_schema import BlobValue as BlobValue, DeleteList as DeleteList, Device as Device, IdList as IdList, LogValue as LogValue, Network as Network, NumberValue as NumberValue, State as State, StringValue as StringValue, XmlValue as XmlValue
from _typeshed import Incomplete
from enum import Enum
from pydantic import BaseModel, ConfigDict, FieldValidationInfo as FieldValidationInfo
from typing import Any, Dict, Iterable, List, Optional, Tuple, Type, Union

def pair_wise(values: Iterable) -> Iterable: ...

ValueUnion: Type
JsonRpc_error_codes: Incomplete

class WappstoObjectType(str, Enum):
    NETWORK: str
    DEVICE: str
    VALUE: str
    STATE: str

ObjectType2BaseModel: Dict[WappstoObjectType, Union[Type[Network], Type[Device], Type[ValueUnion], Type[State]]]

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
    model_config: ConfigDict

class Identifier(BaseModel):
    identifier: Optional[str]
    fast: Optional[bool]

class JsonMeta(BaseModel):
    server_send_time: datetime.datetime

class JsonReply(BaseModel):
    value: Optional[Union[Device, Network, State, ValueUnion, IdList, DeleteList, bool]]
    meta: JsonMeta
    model_config: ConfigDict

class JsonData(BaseModel):
    url: str
    data: Optional[Any]
    meta: Optional[Identifier]
    model_config: ConfigDict
    def path_check(cls, v: str) -> str: ...
    def url_data_mapper(cls, v: Optional[Any], info: FieldValidationInfo) -> Optional[Union[Network, Device, ValueUnion, State, LogValue]]: ...
