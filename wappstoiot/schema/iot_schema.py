import uuid
import datetime

from enum import Enum
from itertools import zip_longest

from typing import Optional
from typing import Union

from pydantic import BaseModel
from pydantic import Extra
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


class WappstoMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PATCH = "PATCH"
    PUT = "PUT"
    DELETE = "DELETE"
    HEAD = "HEAD"


class WappstoObjectType(str, Enum):
    # WappstoMetaType
    NETWORK = "network"
    DEVICE = "device"
    VALUE = "value"
    STATE = "state"


class Success(BaseModel):
    success: bool = True

    class Config:
        extra = Extra.forbid


class Identifier(BaseModel):
    identifier: str


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
        bool  # UNSURE: Do it really return boolean here?
    ]]
    meta: JsonMeta

    class Config:
        extra = Extra.forbid


class JsonData(BaseModel):
    data: Optional[Union[
        Device,
        Network,
        State,
        ValueUnion,
        IdList,
        DeleteList,
    ]]
    url: str
    meta: Optional[Identifier]

    class Config:
        extra = Extra.forbid

    # @validator('url')  # TODO: Make it able to handle queries.
    # def path_check(cls, v, values, **kwargs):
    #     if v.startswith("/services/2.0/"):
    #         selftype, selfid = v.replace("/services/2.0/", "").split('/')
    #         WappstoObjectType(selftype)
    #         uuid.UUID(selfid)
    #     for selftype, selfid in parwise(v.split("/")[1:]):
    #         WappstoObjectType(selftype)
    #         if selfid:
    #             uuid.UUID(selfid)
    #     return v
