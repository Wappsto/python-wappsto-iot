"""Contain the basic JSONRpc structure for the the IoT endpoint."""
import uuid
import datetime

from enum import Enum
from itertools import zip_longest

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type
from typing import Union
from typing import Iterable

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import field_validator
from pydantic import FieldValidationInfo
from pydantic import TypeAdapter

from .base_schema import BlobValue
from .base_schema import Device
from .base_schema import Network
from .base_schema import NumberValue
from .base_schema import State
from .base_schema import LogValue
from .base_schema import StringValue
from .base_schema import XmlValue
from .base_schema import IdList
from .base_schema import DeleteList


def pair_wise(values: Iterable[str]) -> Iterable[Tuple[str, str]]:
    """Pair up the given values, two by two (hands of blue)."""
    a = iter(values)
    return zip_longest(a, a)


ValueUnion: Type = Union[StringValue, NumberValue, BlobValue, XmlValue]


JsonRpc_error_codes = {
    # Rpc Error Code: [HTTP Error Code, "Error String"]
    -32700: [400, "Parse error"],
    -32600: [400, "Invalid Request"],
    -32601: [404, "Method not found"],
    -32602: [400, "Invalid params"],
    -32603: [500, "Internal Server Error"],

    -32000: [404, "Timeout"],
    -32001: [301, "Moved Permanently"],
    -32002: [400, "Bad Request"],
    -32003: [401, "Unauthorized"],
    -32004: [402, "Payment Required"],
    -32005: [403, "Forbidden"],
    -32006: [404, "Not Found"],
    -32007: [405, "Method Not Allowed"],
    -32008: [406, "Not Acceptable"],
    -32009: [408, "Request Timeout"],
    -32010: [409, "Conflict"],
    -32011: [410, "Gone"],
    -32012: [415, "Unsupported Media Type"],
    -32013: [418, "I'm a teapot"],
    -32014: [501, "Not implemented"],
    -32015: [502, "Bad Gateway"],
    -32016: [503, "Service Unavailable"],
    -32017: [504, "Gateway Timeout"],
    -32018: [401, "Queue Limit Reached"]
}


class WappstoObjectType(str, Enum):
    """The different wappsto Object type names, used in a JSONRpc."""

    NETWORK = "network"
    DEVICE = "device"
    VALUE = "value"
    STATE = "state"


ObjectType2BaseModel: Dict[WappstoObjectType, Union[
    Type[Network], Type[Device], Type[ValueUnion], Type[State], Type[LogValue]]
] = {
    WappstoObjectType.NETWORK: Network,
    WappstoObjectType.DEVICE: Device,
    WappstoObjectType.VALUE: ValueUnion,
    WappstoObjectType.STATE: Union[State, LogValue],
}


def url_parser(url: str) -> List[Tuple[WappstoObjectType, Optional[uuid.UUID]]]:
    """Parse the Wappsto Url, for wappsto Type & given UUID."""
    r_list: List[Tuple[WappstoObjectType, Optional[uuid.UUID]]] = []
    obj_type: Optional[WappstoObjectType] = None
    if url is None:
        raise ValueError("Url need to be Set.")
    parsed_url = url.split("?")[0]
    if parsed_url.startswith("/services/2.0/"):
        parsed_url = parsed_url.replace("/services/2.0", "")
    for self_type, self_id in pair_wise(parsed_url.split("/")[1:]):
        obj_type = WappstoObjectType(self_type)
        if self_id:
            r_list.append((obj_type, uuid.UUID(self_id)))
        else:
            r_list.append((obj_type, None))
            break
    return r_list


class WappstoMethod(str, Enum):
    """The different Wappsto methods allowed for the JSONRpc."""

    GET = "GET"
    POST = "POST"
    PATCH = "PATCH"
    PUT = "PUT"
    DELETE = "DELETE"
    HEAD = "HEAD"


class Success(BaseModel):
    """The Default reply on a received JSONRpc."""

    success: bool = True

    model_config: ConfigDict = ConfigDict(extra='forbid')  # type: ignore


class Identifier(BaseModel):
    """The meta data structure for sending data."""

    identifier: Optional[str] = None  # UNSURE: Should this always be there?
    fast: Optional[bool] = None  # Default: False


class JsonMeta(BaseModel):
    """The meta data structure on received data."""

    server_send_time: datetime.datetime


class JsonReply(BaseModel):
    """The JSONRpc param structure for receiving data."""

    value: Optional[Union[
        Device,
        Network,
        State,
        ValueUnion,
        IdList,
        DeleteList,
        bool
    ]]
    meta: JsonMeta

    model_config: ConfigDict = ConfigDict(extra='forbid')  # type: ignore


class JsonData(BaseModel):
    """The JSONRpc param structure for sending."""

    url: str
    data: Optional[Any]
    # data: Optional[Union[
    #     Device,
    #     State,
    #     Network,
    #     ValueUnion,
    #     IdList,
    #     DeleteList,
    # ]]
    meta: Optional[Identifier]

    model_config: ConfigDict = ConfigDict(extra='forbid')  # type: ignore

    @field_validator('url')
    def path_check(cls, v: str) -> str:
        """Ensure that the url is valid."""
        url_parser(v)
        return v

    @field_validator("data", mode='before')
    def url_data_mapper(
        cls, v: Optional[Any], info: FieldValidationInfo
    ) -> Optional[
        Union[
            Network,
            Device,
            ValueUnion,
            State,
            LogValue,
            # IdList,
            # DeleteList,
        ]
    ]:
        """Check & enforce the data schema, depended on the method value."""
        if v is None:
            return v
        if type(v) in ObjectType2BaseModel.values():
            return v

        # TODO: handle IdList & DeleteList

        url_obj = url_parser(info.data['url'])
        obj_type = url_obj[-1][0]

        model = ObjectType2BaseModel[obj_type]
        if model is None:
            raise ValueError('Unhandled Object type.')

        if isinstance(model, BaseModel):
            return model.model_validate(v)

        model_converter: TypeAdapter = TypeAdapter(model)  # type: ignore
        return model_converter.validate_python(v)
