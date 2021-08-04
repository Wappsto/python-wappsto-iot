"""
## https://www.jsonrpc.org/specification


-> {"jsonrpc": "2.0", "method": "ping", "id": "foo"}
<- {"jsonrpc": "2.0", "result": "pong", "id": "foo"}


--> {'jsonrpc': '2.0', 'method': 'cat', 'params': {'name': 'Yoko'}, 'id': 1}

<--
{
  "id": 1,
  "jsonrpc": "2.0",
  "result": [
    {
      "uuid": 7,
      "name": "fluffy",
      "breed": "poodle"
    }
  ]
}



--> {"jsonrpc": "2.0", "method": "update", "params": [1,2,3,4,5]}
--> {"jsonrpc": "2.0", "method": "foobar"}


<-- {"jsonrpc": "2.0", "error": {
        "code": -32601, "message": "Method not found"
    }, "id": "1"}

<-- {"jsonrpc": "2.0", "error": {
        "code": -32601, "message": "Method not found", "data": ""
    }, "id": "1"}

"""
import json
import logging
import random
import string

from contextlib import contextmanager

from pydantic import BaseModel
from pydantic import Extra
from pydantic import parse_obj_as
from pydantic import ValidationError
from pydantic.fields import ModelField

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from enum import Enum


from Connection.Templates import ConnectionClass


class RpcVersion(str, Enum):
    v2_0 = "2.0"


class RpcErrorCode(Enum):
    """
    Error Codes:    Error code:         Message Description:
    ---
        -32700      Parse error         Invalid JSON was received by the server.
                                        An error occurred on the server while parsing the JSON text.
        -32600      Invalid Request     The JSON sent is not a valid Request object.
        -32601      Method not found    The method does not exist / is not available.

        -32602      Invalid params      Invalid method parameter(s).
        -32603      Internal error      Internal JSON-RPC error.
        -32000      Server error        IconServiceEngine internal error.
          ...
        -32099      Server error        IconServiceEngine internal error.
    """
    ParseError = -32700
    InvalidRequest = -32600
    MethodNotFound = -32601
    InvalidParams = -32602
    InternalError = -32603
    ServerError = -32000


class BaseRPC(BaseModel):
    jsonrpc: RpcVersion
    id: Union[str, int]

    class Config:
        extra = Extra.forbid


class RPCNotification(BaseModel):
    jsonrpc: RpcVersion
    method: str
    params: Optional[Any]

    class Config:
        extra = Extra.forbid

    @classmethod
    def update_method(cls, new_type: Enum):
        """
        Update the Method schema, to fit the new one.
        """
        new_fields = ModelField.infer(
            name="method",
            value=...,
            annotation=new_type,
            class_validators=None,
            config=cls.__config__
        )
        cls.__fields__['method'] = new_fields
        cls.__annotations__['method'] = new_type


class RPCRequest(BaseRPC):
    params: Optional[Any]
    method: str

    @classmethod
    def update_method(cls, new_type: Enum):
        """
        Update the Method schema, to fit the new one.
        """
        new_fields = ModelField.infer(
            name="method",
            value=...,
            annotation=new_type,
            class_validators=None,
            config=cls.__config__
        )
        cls.__fields__['method'] = new_fields
        cls.__annotations__['method'] = new_type


class ErrorModel(BaseModel):
    code: RpcErrorCode
    message: str
    data: Optional[Any]

    class Config:
        extra = Extra.forbid


class RPCError(BaseRPC):
    error: ErrorModel


class RPCSuccess(BaseRPC):
    result: Any

    @classmethod
    def update_result(cls, new_type: Enum):
        """
        Update the Method schema, to fit the new one.
        """
        new_fields = ModelField.infer(
            name="result",
            value=...,
            annotation=new_type,
            class_validators=None,
            config=cls.__config__
        )
        cls.__fields__['result'] = new_fields
        cls.__annotations__['result'] = new_type


JsonSchemas = Union[
    RPCError,
    RPCNotification,
    RPCRequest,
    RPCSuccess,
]


class JsonRpc:  # Unsure(MBK): Are template a good idea here?
    def __init__(
        self,
        connection: ConnectionClass,
        session_id: str = "",
        methods: Optional[Enum] = None,
        results: Optional[Any] = None,
    ):
        self.log = logging.getLogger(__name__)
        self.log.addHandler(logging.NullHandler())

        self.connection = connection

        if methods:
            RPCNotification.update_method(methods)
            RPCRequest.update_method(methods)

        if results:
            RPCSuccess.update_result(results)

        self.batch_lock: bool = False
        self.session_count: int = 0
        self.session_id: str = session_id if session_id else "".join(
            random.choices(string.ascii_letters + string.digits, k=10)
        )
        self.batched_list: List[Dict[Any, Any]] = []

    def data_handling(self):
        """
        Placeholder.

        If a list of RPC's from server.
        create a dictionary with RpcIDs as keys,
        that are checked every time, something is received to be send.
        When the Dictionary with RPC List are full, it is send.

        """
        pass

    def __ValidationError2ErrorModel(
        self,
        errors: List[Dict[str, Union[List[str], str, Dict[str, List[str]]]]]
    ) -> Union[ErrorModel, None]:
        # TODO(MBK): Make a algorithmic to prioritize the Errors.

        # This order?
        # 1) Method Not Found (Everything right except Method.)
        # 2) Invalid Parameter(s) (If the Data or values are wrong?)
        # 3) Invalid Request (Missing/Extra Keys or not a JSON/RPC)

        self.errors = errors  # TODO(MBK): Remove me!
        # any( {'enum_values': ["2.0"]} in err.values() for err in errors)
        # filter(lambda x: {'enum_values': ["2.0"]} in x.values(), errors)

        e_type = errors[0]
        if e_type['type'] in ["value_error.missing", "value_error.extra"]:
            return ErrorModel(
                code=RpcErrorCode.InvalidRequest,
                message="Invalid Request",
                data=e_type
            )
        elif e_type['type'] == "type_error.enum":

            if "method" in e_type["loc"]:
                return ErrorModel(
                    code=RpcErrorCode.MethodNotFound,
                    message="Method Not Found",
                    data=e_type
                )

            return ErrorModel(
                code=RpcErrorCode.InvalidParams,
                message="Invalid parameter(s)",
                data=e_type
            )

            # TODO(MBK): Handle when RPCSuccess->result is wrong, exception.
            #            If that happens... 'Invalid paramter'?

        return None

    def _parse_data(
        self,
        data: Union[str, bytes]
    ) -> Union[RPCNotification, RPCRequest, RPCError, RPCSuccess]:
        try:
            j_data = json.loads(data)
            p_data: JsonSchemas = parse_obj_as(
                JsonSchemas,  # type: ignore
                j_data
            )
        except json.JSONDecodeError:
            return RPCError(
                id=None,
                jsonrpc=RpcVersion("2.0"),
                error=ErrorModel(
                    code=RpcErrorCode.ParseError,
                    message="Parse error",
                    data=data
                ),
            )
        except ValidationError as error:
            error_package = self.__ValidationError2ErrorModel(
                errors=error.errors()
            )

            if not error_package:
                self.log.exception("Unhanded ValidationError.")
                raise

            return RPCError(
                id=j_data.get('id'),
                jsonrpc=RpcVersion("2.0"),
                error=error_package
            )

        return p_data

    # def _parse_data2(
    #     self,
    #     data: Union[str, bytes]
    # ) -> Union[RPCNotification, RPCRequest, RPCError, RPCSuccess]:
    #     for schema in [RPCSuccess, RPCNotification, RPCRequest, RPCError]:
    #         try:
    #             r_data = schema.parse_raw(data)
    #         except ValidationError as error:
    #             e_type = error.errors()[0]['type']

    #             if e_type == "value_error.jsondecode":
    #                 return
    #             elif e_type == "value_error.missing":
    #                 continue
    #             elif e_type == "value_error.extra":
    #                 continue
    #             elif e_type == "value_error.enum":
    #                 continue
    #         return r_data

    def _id_count(self, method: Enum):
        """Create an unique Rpc-id."""
        self.session_count += 1
        return f"{self.session_id}_{method}_{self.session_count}"

    def result(self, RpcID: str, data: Any) -> None:
        """
        Send a Result JsonRpc.

        Note: This is affected of the 'Batch' Scope,
              if the data is anything but 'True'.

        Args:
            RpcID: The ID of the requests, that this is a result of.
            data: The result data.
        """

        package = RPCSuccess(
            id=RpcID,
            jsonrpc=RpcVersion("2.0"),
            result=data
        )

        if self.batch_lock and data is not True:
            self.batched_list.append(package.dict())
        else:
            self.connection.send(package.json().encode('utf-8'))

    def request(self, method: Enum, data: Any) -> None:
        """
        Send a Request JsonRpc.

        Note: This is affected of the 'Batch' Scope.
        """
        package = RPCRequest(
            id=self._id_count(method),
            jsonrpc=RpcVersion("2.0"),
            method=method,
            params=data
        )
        if self.batch_lock:
            self.batched_list.append(package.dict())
        else:
            self.connection.send(package.json().encode('utf-8'))

    def error(
        self,
        RpcID: str,
        errorCode: RpcErrorCode,
        msg: str,
        data: Optional[Any] = None
    ):
        """
        Send a Error JsonRpc.
        """
        package = RPCError(
            id=RpcID,
            jsonrpc=RpcVersion("2.0"),
            error=ErrorModel(
                code=errorCode,
                message=msg,
                data=data
            ),
        )

        self.connection.send(package.json().encode('utf-8'))
    
    def success(self, RpcID: str):
        """
        Send a Success JsonRpc.

        # NOTE: A Wappsto JSON thing. should be removed.
        #       And replaced by the Result function.
        """
        self.result(RpcID=RpcID, data=True)

    def notification(
        self,
        method: Union[Enum, str],
        data: Optional[Any] = None
    ):
        """
        Send a notification JsonRpc.

        A Notification, do not ticker a reply from the server.

        Args:
            method: The JSON/RPC Method that should be used.
            data: (optional) The data to be send with given method.
        """
        package = RPCNotification(
            method=method,
            params=data
        )

        self.connection.send(package.json().encode('utf-8'))

    def __send_batch(self):
        """Send all the JSON/RPC stored in the batched list."""
        self.connection.send(json.dumps(self.batched_list).encode('utf-8'))
        self.batched_list.clear()

    @contextmanager
    def batch(self):
        """
        Batch all RPC's called within the scope, into one RPC-List.
        """
        # UNSURE(MBK): Should this be a lock, or a count to make it multiple
        #              use safe?
        self.batch_lock = True
        try:
            yield
        finally:
            self.batch_lock = False
            self.__send_batch()


# from Protocol.rpc import *
# class WappstoMethods(str, Enum):
#     """
#     The JSON/RPC methods that the Wappsto are using.
#     """
#     delete = "DELETE"
#     put = "PUT"
#     post = "POST"
#     get = "GET"
# RpcTing = JsonRpc(WappstoMethods, lambda *args, **kwargs: print(f"{args=}{kwargs=}"))
# RpcTing._parse_data('{"jsonrpc": "1.0", "method": "PUT", "id": "ksj"}')
