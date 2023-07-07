import uuid
import datetime

from enum import Enum
from itertools import zip_longest

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
# from typing import Type
from typing import Union

from pydantic import BaseModel
from pydantic import Extra
from pydantic import parse_obj_as
from pydantic import validator

from .base_schema import BlobValue
from .base_schema import Device
from .base_schema import Network
from .base_schema import NumberValue
from .base_schema import State
from .base_schema import StringValue
from .base_schema import XmlValue
from .base_schema import IdList
from .base_schema import DeleteList


def parwise(values):
    a = iter(values)
    return zip_longest(a, a)


ValueUnion = Union[StringValue, NumberValue, BlobValue, XmlValue]

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
    # WappstoMetaType
    NETWORK = "network"
    DEVICE = "device"
    VALUE = "value"
    STATE = "state"


ObjectType2BaseModel: Dict[WappstoObjectType, Any] = {
    WappstoObjectType.NETWORK: Network,
    WappstoObjectType.DEVICE: Device,
    WappstoObjectType.VALUE: ValueUnion,
    WappstoObjectType.STATE: State,
}


def url_parser(url: str) -> List[Tuple[WappstoObjectType, Optional[uuid.UUID]]]:
    r_list: List[Tuple[WappstoObjectType, Optional[uuid.UUID]]] = []
    obj_type: Optional[WappstoObjectType] = None
    if url is None:
        raise ValueError("Url need to be Set.")
    parsed_url = url.split("?")[0]
    if parsed_url.startswith("/services/2.0/"):
        parsed_url = parsed_url.replace("/services/2.0", "")
    for selftype, selfid in parwise(parsed_url.split("/")[1:]):
        obj_type = WappstoObjectType(selftype)
        if selfid:
            r_list.append((obj_type, uuid.UUID(selfid)))
        else:
            r_list.append((obj_type, None))
            break
    return r_list


class WappstoMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PATCH = "PATCH"
    PUT = "PUT"
    DELETE = "DELETE"
    HEAD = "HEAD"


class Success(BaseModel):
    success: bool = True

    class Config:
        extra = Extra.forbid


class Identifier(BaseModel):
    identifier: Optional[str]  # UNSURE: Should this always be there?
    fast: Optional[bool]  # Default: False


class JsonMeta(BaseModel):
    server_send_time: datetime.datetime


class JsonReply(BaseModel):
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

    class Config:
        extra = Extra.forbid

    # @validator("value", pre=True, always=True)
    # def url_data_mapper(
    #     cls, v, values, **kwargs
    # ) -> Optional[Union[
    #         Network,
    #         Device,
    #         ValueUnion,
    #         State,
    #         IdList,
    #         DeleteList,
    #         bool
    #     ]
    # ]:
    #     """Check & enforce the data schema, depended on the method value."""
    #     if v is None or isinstance(v, bool):
    #         return v
    #     if type(v) in ObjectType2BaseModel.values():
    #         return v

    #     # TODO: handle IdList & DeleteList

    #     url_obj = url_parser(values.get('url'))
    #     obj_type = url_obj[-1][0]

    #     model = ObjectType2BaseModel[obj_type]
    #     if model is None:
    #         raise ValueError('Unhandled Object type.')
    #     return parse_obj_as(model, v)


class JsonData(BaseModel):
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

    class Config:
        extra = Extra.forbid

    @validator('url')
    def path_check(cls, v, values, **kwargs):
        url_parser(v)
        return v

    @validator("data", pre=True, always=True)
    def url_data_mapper(
        cls, v, values, **kwargs
    ) -> Optional[
        Union[
            Network,
            Device,
            ValueUnion,
            State,
            IdList,
            DeleteList,
        ]
    ]:
        """Check & enforce the data schema, depended on the method value."""
        if v is None:
            return v
        if type(v) in ObjectType2BaseModel.values():
            return v

        # TODO: handle IdList & DeleteList

        url_obj = url_parser(values.get('url'))
        obj_type = url_obj[-1][0]

        model = ObjectType2BaseModel[obj_type]
        if model is None:
            raise ValueError('Unhandled Object type.')
        return parse_obj_as(model, v)
