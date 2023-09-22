"""Contain the IoT Api that handle the data conversion."""
import copy
import json
import logging
import pathlib
import re
import threading

from uuid import UUID
from pathlib import Path

from concurrent.futures import ThreadPoolExecutor

from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

import slxjsonrpc
from slxjsonrpc.schema.jsonrpc import ErrorModel

from .template import StatusID
from .template import ServiceClass

from ..schema.base_schema import Device
from ..schema.base_schema import IdList
from ..schema.base_schema import LogValue
from ..schema.base_schema import Network
from ..schema.base_schema import State
from ..schema.base_schema import ValueUnion
from ..schema.base_schema import WappstoObject

from ..schema.iot_schema import JsonData
from ..schema.iot_schema import Identifier
from ..schema.iot_schema import JsonReply
from ..schema.iot_schema import Success
from ..schema.iot_schema import WappstoMethod
# from ..schema.iot_schema import WappstoObjectType

from ..utils.certificateread import certificate_info_extraction
from ..utils import observer

from ..connections.sslsocket import TlsSocket
from ..connections.protocol import Connection


RpcSchemas = Union[
    slxjsonrpc.RpcBatch,
    slxjsonrpc.RpcError,
    slxjsonrpc.RpcNotification,
    slxjsonrpc.RpcRequest,
    slxjsonrpc.RpcResponse,
]

# POST   -> onCreate
# GET    -> onRefresh
# PUT    -> onChange
# DELETE -> onDelete

# create  -> POST
# refresh -> GET
# change  -> PUT
# delete  -> DELETE


class IoTAPI(ServiceClass):
    """IoTAPI, handle the conversion of the data from the socket and UI."""

    wappstoPort = {
        "dev": 52005,
        "qa": 53005,
        "staging": 54005,
        "prod": 443
    }

    def __init__(
        self,
        ca: Path,
        crt: Path,
        key: Path,
        worker_count: int = 2,
        fast_send: bool = False,
    ):
        """."""
        self.log = logging.getLogger(__name__)
        self.log.addHandler(logging.NullHandler())
        self.ca = ca
        self.crt = crt
        self.key = key

        self.timeout = 3

        self.fast_send = fast_send

        self.addr, self.port = self._url_gen(self.crt)

        self.connection: Connection

        self.connection = TlsSocket(
            address=self.addr,
            port=self.port,
            ca=self.ca,
            crt=self.crt,
            key=self.key
        )

        params = {
            x: JsonData for x in WappstoMethod
        }

        result = {
            WappstoMethod.GET: Union[JsonReply, Success],
            WappstoMethod.POST: Union[JsonReply, Success],
            WappstoMethod.PUT: Union[JsonReply, Success],
            WappstoMethod.DELETE: Union[JsonReply, Success],
            # WappstoMethod.PATCH: Union[JsonReply, Success],
            WappstoMethod.HEAD: Union[JsonReply, Success],
        }

        self.subscribers: Dict[
            UUID,
            List[Union[
                Callable[[Network, WappstoMethod], None],
                Callable[[Device, WappstoMethod], None],
                Callable[[ValueUnion, WappstoMethod], None],
                Callable[[State, WappstoMethod], None],
            ]]
        ] = {}

        method_cb = {
            WappstoMethod.GET: self._get,
            WappstoMethod.POST: self._post,
            # WappstoMethod.PATCH: self._patch,
            WappstoMethod.PUT: self._put,
            WappstoMethod.DELETE: self._delete,
            # WappstoMethod.HEAD: self._head,
        }

        self.connection.connect()

        self.jsonrpc = slxjsonrpc.SlxJsonRpc(
            methods=WappstoMethod,
            method_cb=method_cb,
            result=result,
            params=params,
        )
        self.jsonrpc._verbose = True

        self.killed = threading.Event()
        self.workers = ThreadPoolExecutor(max_workers=worker_count)

        self.workers.submit(self._receive_handler)

    def close(self) -> None:
        """Closes the IoTApi down."""
        self.killed.set()
        self.log.debug("Closing Connection.")
        self.connection.close()
        self.log.debug("Closing Workers")
        # while self.workers._work_queue.qsize() > 1:
        #     time.sleep(0.02)
        self.workers.shutdown()
        self.log.debug("IoTAPI Closed.")

    # #########################################################################
    #                              Helper Methods
    # #########################################################################

    def _url_gen(self, crt: pathlib.Path) -> Tuple[str, int]:
        cer = certificate_info_extraction(crt_path=crt)
        endpoint = cer.get('issuer', {}).get('commonName')
        port = self.wappstoPort.get(endpoint.split('.')[0], 443)
        if endpoint.split('.')[0] in self.wappstoPort.keys():
            addr = endpoint
        else:
            addr = f"collector.{endpoint}"

        if re.search(r'^[A-Za-z0-9+.-]+://', addr):
            addr = addr.split("://", maxsplit=1)[-1]
        # if not re.search(r':[0-9]+', addr):
        #     addr = f'{addr}:{port}'
        return (addr, port)

    def _receive_handler(self) -> None:
        self.log.debug("Receive Handler Started!")
        while not self.killed.is_set():
            try:
                data = self.connection.receive(parser=json.loads)

                if not data:
                    continue

                if isinstance(data, str):
                    self.log.warning(f'Received non JSONRPC data: {data}')
                    continue

                if not isinstance(data, list):
                    data = [data]
                for elemt in data:
                    _ids = [elemt.get('id', elemt) for elemt in data]
                    self.log.debug(f"Package received: {elemt.get('id', elemt)}")

                reply = self.jsonrpc.parser(data)
                self.log.debug(f"Package ID: {_ids}; Reply: {reply}")

                if not reply:
                    continue

                self._send_logic(reply)
                # UNSURE: How do we check if it was send?
                observer.post(StatusID.SEND, reply)

            except Exception:
                self.log.error(f"data: {data}")
                self.log.exception("Receive Handler Error:")
        self.log.debug("Receive Handler Stopped!")

    def _send_logic(self, data: RpcSchemas) -> None:
        # NOTE (MBK): Something do not work here!
        # if not data:
        #     return
        with self.connection.send_ready:  # NOTE: Waiting here, until ready!
            with self.jsonrpc.batch():
                batch_size = self.jsonrpc.batch_size()
                if batch_size:
                    send_data = self.jsonrpc.get_batch_data(data)
                    self.log.debug(f"Batching: {batch_size}")
                else:
                    send_data = copy.copy(data)

                if isinstance(send_data, slxjsonrpc.RpcBatch):
                    _id = "; ".join(x.id for x in send_data.root)
                elif send_data:
                    _id = send_data.id

                if _id:
                    self.log.debug(f"Package ID: {_id};")

                if send_data:
                    observer.post(StatusID.SENDING, send_data)
                    self.connection.send(send_data.model_dump_json(exclude_none=True))

    def _resend_data(self, data: Union[str, bytes]) -> None:
        j_data = json.loads(data)
        _cb_event = threading.Event()

        if not isinstance(j_data, list):
            j_data = [j_data]

        for l_data in j_data:
            rpc_id = l_data.get('id')

            if l_data.get('params'):
                s_data = self.jsonrpc.create_request(
                    callback=lambda data: _cb_event.set(),
                    error_callback=lambda err_data: _cb_event.set(),
                    method=l_data.get('method'),
                    params=l_data.get('params')
                )
                self._send_logic(s_data)
            elif l_data.get('result'):
                self.jsonrpc._id_cb[rpc_id] = lambda data: _cb_event.set()
                self.jsonrpc._id_error_cb[rpc_id] = lambda err_data: _cb_event.set()
                self.jsonrpc._id_method[rpc_id] = l_data.get('method')
                # self.jsonrpc._add_result_handling(  # NOTE: slxJsonRpc v0.8.1.
                #     method=l_data.get('method'),
                #     _id=rpc_id,
                #     callback=lambda data: _cb_event(),
                #     error_callback=lambda err_data: _cb_event(),
                # )
                s_data = self.jsonrpc._parse_data(l_data)
                self._send_logic(s_data)

            self.log.debug(f"--CALLBACK Ready! {rpc_id}")
            if _cb_event.wait(timeout=self.timeout):
                self.log.debug(f"--CALLBACK EVENT! {rpc_id}")
                observer.post(StatusID.SEND, s_data)
            else:
                self.log.debug(f"--CALLBACK None! {rpc_id}")
                observer.post(StatusID.SENDERROR, s_data)
        return None

    # -------------------------------------------------------------------------
    #                               API Helpers
    # -------------------------------------------------------------------------

    def __create_json_data(
        self,
        data: List[Any],
        url: str,
        method: WappstoMethod,
    ) -> RpcSchemas:
        _cb_event = threading.Event()
        _err_data: Optional[ErrorModel] = None

        def _err_callback(err_data: ErrorModel) -> None:
            nonlocal _err_data
            nonlocal _cb_event
            _err_data = err_data
            _cb_event.set()

        with self.jsonrpc.batch():
            for values in data:
                j_data = JsonData(
                    data=values,
                    url=url,
                    meta=Identifier(fast=True, identifier=None)
                    if self.fast_send and method != WappstoMethod.GET
                    else None
                )

                self.log.debug(f"Sending for: {url}")

                self.jsonrpc.create_request(
                    method=method,
                    callback=lambda data: _cb_event.set(),
                    error_callback=_err_callback,
                    params=j_data
                )

        rpc_data = self.jsonrpc.get_batch_data()

        return rpc_data, _cb_event, _err_data

    def _no_reply_bulk_send(
        self,
        data: List[Any],
        url: str,
        method: WappstoMethod,
    ) -> bool:
        rpc_data, _cb_event, _err_data = self.__create_json_data(
            data=data, url=url, method=method,
        )
        rpc_id = "[" + ",".join(
            [f'"{getattr(rpc_data, "id", None)}"' for rpc_d in rpc_data]
        ) + "]"

        self._send_logic(rpc_data)

        self.log.debug(f"--CALLBACK Ready! {rpc_id}")
        if _cb_event.wait(timeout=self.timeout):
            if _err_data:
                self.log.debug(f"--CALLBACK Error! {_err_data}")
                observer.post(StatusID.ERROR, _err_data)
                # raise ConnectionError(_err_data.message)
                return False
            self.log.debug(f"--CALLBACK EVENT! {rpc_id}")
            observer.post(StatusID.SEND, rpc_data)
            return True
        observer.post(StatusID.SENDERROR, rpc_data)
        self.log.debug(f"--CALLBACK None! {rpc_id}")
        raise TimeoutError(f'JsonRPC reply timeout on package: {rpc_id}')

    def _no_reply_send(
        self,
        data: Optional[Union[WappstoObject, LogValue]],
        url: str,
        method: WappstoMethod,
    ) -> bool:
        j_data = JsonData(
            data=data,
            url=url,
            meta=Identifier(fast=True, identifier=None)
            if self.fast_send and method != WappstoMethod.GET else None
        )

        self.log.debug(f"Sending for: {url}")

        _cb_event = threading.Event()
        _err_data: Optional[ErrorModel] = None

        def _err_callback(err_data: ErrorModel) -> None:
            nonlocal _err_data
            nonlocal _cb_event
            _err_data = err_data
            _cb_event.set()

        rpc_data = self.jsonrpc.create_request(
            method=method,
            callback=lambda data: _cb_event.set(),
            error_callback=_err_callback,
            params=j_data
        )

        rpc_id = getattr(rpc_data, 'id', None)

        self._send_logic(rpc_data)

        self.log.debug(f"--CALLBACK Ready! {rpc_id}")
        if _cb_event.wait(timeout=self.timeout):
            if _err_data:
                self.log.debug(f"--CALLBACK Error! {_err_data}")
                observer.post(StatusID.ERROR, _err_data)
                # raise ConnectionError(_err_data.message)
                return False
            self.log.debug(f"--CALLBACK EVENT! {rpc_id}")
            observer.post(StatusID.SEND, rpc_data)
            return True
        observer.post(StatusID.SENDERROR, rpc_data)
        self.log.debug(f"--CALLBACK None! {rpc_id}")
        raise TimeoutError(f'JsonRPC reply timeout on package: {rpc_id}')

    def _reply_send(
        self,
        data: Optional[WappstoObject],
        url: str,
        method: WappstoMethod,
    ) -> Optional[WappstoObject]:
        j_data = JsonData(
            data=data,
            url=url,
            meta=Identifier(fast=True, identifier=None)
            if self.fast_send and method != WappstoMethod.GET else None
        )

        self.log.debug(f"Sending for: {url}")

        _cb_event = threading.Event()
        _err_data: ErrorModel = None

        def _err_callback(err_data: ErrorModel) -> None:
            nonlocal _err_data
            nonlocal _cb_event
            _err_data = err_data
            _cb_event.set()

        _data: Optional[JsonReply] = None

        def _data_callback(data: JsonReply) -> None:
            nonlocal _data
            nonlocal _cb_event
            _data = data
            _cb_event.set()

        rpc_data = self.jsonrpc.create_request(
            method=method,
            callback=_data_callback,
            error_callback=_err_callback,
            params=j_data
        )

        rpc_id = getattr(rpc_data, 'id', None)

        self._send_logic(rpc_data)

        self.log.debug(f"--CALLBACK Ready! {rpc_id}")
        if _cb_event.wait(timeout=self.timeout):
            if _data:
                self.log.debug(f"--CALLBACK EVENT! {rpc_id}")
                observer.post(StatusID.SEND, rpc_data)
                return _data.value
            if _err_data:
                self.log.warning(f"--CALLBACK Error! {_err_data}")
                observer.post(StatusID.ERROR, _err_data)
                # raise ConnectionError(_err_data.message)
                return None
        self.log.debug(f"--CALLBACK None! {rpc_id}")
        observer.post(StatusID.SENDERROR, rpc_data)
        raise TimeoutError(f'JsonRPC reply timeout on package: {rpc_id}')

    # -------------------------------------------------------------------------
    #                              Callback Helpers
    # -------------------------------------------------------------------------

    def _cb_handler(self, data: JsonData, method: WappstoMethod) -> None:
        object_uuid = UUID(data.url.split("/")[-1])
        self.log.debug(f"Object UUID: {object_uuid}")
        for cb in self.subscribers.get(object_uuid, [self._default_cb]):
            self.workers.submit(cb, data.data, method)
            self.log.debug(f"Submitted to Worker: {cb}")

    def _default_cb(self, data: WappstoObject, method: WappstoMethod) -> None:
        self.log.warning(
            f"No callback found for method: {method}; data {data}"
        )

    # #########################################################################
    #                              Callback Methods
    # #########################################################################

    def _get(self, data: JsonData) -> Union[Success, JsonData]:
        # Add data and callback-function to a threadpool.
        self.log.debug("_get: Called!")
        self._cb_handler(data=data, method=WappstoMethod.GET)
        return Success()

    def _post(self, data: JsonData) -> Union[Success, JsonData]:
        # Add data and callback-function to a threadpool.
        self.log.debug("_post: Called!")
        self._cb_handler(data=data, method=WappstoMethod.POST)
        return Success()

    def _put(self, data: JsonData) -> Union[Success, JsonData]:
        # Add data and callback-function to a threadpool.
        self.log.debug("_put: Called!")
        self._cb_handler(data=data, method=WappstoMethod.PUT)
        return Success()

    def _delete(self, data: JsonData) -> Union[Success, JsonData]:
        # Add data and callback-function to a threadpool.
        self.log.debug("_delete: Called!")
        self._cb_handler(data=data, method=WappstoMethod.DELETE)
        return Success()

    # def _patch(self, data: JsonData) -> Union[Success, JsonData]:
    #     # Add data and callback-function to a threadpool.
    #     self.log.debug("_patch: Called!")
    #     self._cb_handler(data=data, method=WappstoMethod.PATCH)
    #     return Success()

    # def _head(self, data: JsonData) -> Union[Success, JsonData]:
    #     # Add data and callback-function to a threadpool.
    #     self.log.debug("_head: Called!")
    #     self._cb_handler(data=data, method=WappstoMethod.HEAD)
    #     return Success()

    # #########################################################################
    #                               Helper API
    # #########################################################################

    def ping(self) -> None:
        """Sends a ping to check the connection."""
        return self._no_reply_send(
            data=None,
            url="/network",
            method=WappstoMethod.HEAD
        )

    # #########################################################################
    #                               Network API
    # #########################################################################

    def subscribe_network_event(
        self,
        uuid: UUID,
        callback: Callable[[Network, WappstoMethod], None]
    ) -> None:
        """Subscribe a function to be call on Network changes."""
        self.subscribers.setdefault(uuid, []).append(callback)

    def unsubscribe_network_event(
        self,
        uuid: UUID,
        callback: Callable[[Network, WappstoMethod], None]
    ) -> None:
        """Unsubscribe a function from Network changes."""
        self.subscribers.get(uuid, []).remove(callback)

    def post_network(self, data: Network) -> bool:
        """Create the network."""
        return self._no_reply_send(
            data=data,
            url="/network/",
            method=WappstoMethod.POST
        )

    def put_network(self, uuid: UUID, data: Network) -> bool:
        """Make changes to a network."""
        return self._no_reply_send(
            data=data,
            url=f"/network/{uuid}",
            method=WappstoMethod.PUT
        )

    def get_network(self, uuid: UUID) -> Optional[Network]:
        """Request the network data."""
        return self._reply_send(
            data=None,  # NOTE: Should be nonexistent or Null.
            url=f"/network/{uuid}",
            method=WappstoMethod.GET
        )

    def delete_network(self, uuid: UUID) -> bool:
        """Remove the network."""
        return self._no_reply_send(
            data=None,  # NOTE: Should be nonexistent or Null.
            url=f"/network/{uuid}",
            method=WappstoMethod.DELETE
        )

    # #########################################################################
    #                                Device API
    # #########################################################################

    def subscribe_device_event(
        self,
        uuid: UUID,
        callback: Callable[[Device, WappstoMethod], None]
    ) -> None:
        """Subscribe a function to be call on given Device changes."""
        self.subscribers.setdefault(uuid, []).append(callback)

    def unsubscribe_device_event(
        self,
        uuid: UUID,
        callback: Callable[[Device, WappstoMethod], None]
    ) -> None:
        """Unsubscribe a function from given Device changes."""
        self.subscribers.get(uuid, []).remove(callback)

    def post_device(self, network_uuid: UUID, data: Device) -> bool:
        """Create given device."""
        return self._no_reply_send(
            data=data,
            url=f"/network/{network_uuid}/device/",
            method=WappstoMethod.POST
        )

    def put_device(self, uuid: UUID, data: Device) -> bool:
        """Make changes to a device."""
        return self._no_reply_send(
            data=data,
            url=f"/device/{uuid}",
            method=WappstoMethod.PUT
        )

    def get_device_where(self, network_uuid: UUID, **kwargs: str) -> Optional[UUID]:
        """Request data from a device with given values."""
        # /network/{uuid}/device?this_name==X
        key, value = list(kwargs.items())[0]
        url = f"/network/{network_uuid}/device?this_{key}=={value}"
        data: IdList = self._reply_send(
            data=None,
            url=url,
            method=WappstoMethod.GET
        )

        temp = getattr(data, "id", None)
        if not temp:
            return None
        return temp[0]

    def get_device(self, uuid: UUID) -> Union[Device, None]:
        """Request to get given device data."""
        return self._reply_send(
            data=None,
            url=f"/device/{uuid}",
            method=WappstoMethod.GET
        )

    def delete_device(self, uuid: UUID) -> bool:
        """Remove to given device."""
        return self._no_reply_send(
            data=None,
            url=f"/device/{uuid}",
            method=WappstoMethod.DELETE
        )

    # #########################################################################
    #                                 Value API
    # #########################################################################

    def subscribe_value_event(
        self,
        uuid: UUID,
        callback: Callable[[ValueUnion, WappstoMethod], None]
    ) -> None:
        """Subscribe a function to be call on given value changes."""
        self.subscribers.setdefault(uuid, []).append(callback)

    def unsubscribe_value_event(
        self,
        uuid: UUID,
        callback: Callable[[ValueUnion, WappstoMethod], None]
    ) -> None:
        """Unsubscribe a function from given value changes."""
        self.subscribers.get(uuid, []).remove(callback)

    def post_value(self, device_uuid: UUID, data: ValueUnion) -> bool:
        """Create given value."""
        # url=f"/services/2.0/{uuid}/value",
        return self._no_reply_send(
            data=data,
            url=f"/device/{device_uuid}/value/",
            method=WappstoMethod.POST
        )

    def put_value(self, uuid: UUID, data: ValueUnion) -> bool:
        """Make changes to a value."""
        # url=f"/services/2.0/value/{uuid}",
        return self._no_reply_send(
            data=data,
            url=f"/value/{uuid}",
            method=WappstoMethod.PUT
        )

    def get_value_where(self, device_uuid: UUID, **kwargs: str) -> Optional[UUID]:
        """Request data from a value with given values."""
        # /network/{uuid}/device?this_name==X
        key, value = list(kwargs.items())[0]
        url = f"/device/{device_uuid}/value?this_{key}=={value}"
        data: IdList = self._reply_send(
            data=None,
            url=url,
            method=WappstoMethod.GET
        )

        temp: Optional[List[UUID]] = getattr(data, "id", None)
        if not temp:
            return None
        return temp[0]

    def get_value(self, uuid: UUID) -> Union[ValueUnion, None]:
        """Request to get given value data."""
        # url=f"/services/2.0/value/{uuid}",
        return self._reply_send(
            data=None,
            url=f"/value/{uuid}",
            method=WappstoMethod.GET
        )

    def delete_value(self, uuid: UUID) -> bool:
        """Remove to given value."""
        # url=f"/services/2.0/value/{uuid}",
        return self._no_reply_send(
            data=None,
            url=f"/value/{uuid}",
            method=WappstoMethod.DELETE
        )

    # #########################################################################
    #                                State API
    # #########################################################################

    def subscribe_state_event(
        self,
        uuid: UUID,
        callback: Callable[[State, WappstoMethod], None]
    ) -> None:
        """Subscribe a function to be call on given state changes."""
        self.subscribers.setdefault(uuid, []).append(callback)

    def unsubscribe_state_event(
        self,
        uuid: UUID,
        callback: Callable[[State, WappstoMethod], None]
    ) -> None:
        """Unsubscribe a function from given state changes."""
        self.subscribers.get(uuid, []).remove(callback)

    def post_state(self, value_uuid: UUID, data: Union[State, LogValue]) -> bool:
        """Create given state."""
        # url=f"/services/2.0/{uuid}/state",
        return self._no_reply_send(
            data=data,
            url=f"/value/{value_uuid}/state/",
            method=WappstoMethod.POST
        )

    def put_bulk_state(self, uuid: UUID, data: List[LogValue]) -> bool:
        """Make bulk changes the given state."""
        # url=f"/services/2.0/state/{uuid}",
        try:
            return self._no_reply_bulk_send(
                data=data,
                url=f"/state/{uuid}",
                method=WappstoMethod.PUT
            )
        except TimeoutError:
            msg = (
                'Error in sending Values.\n'
                'If Offline storage is enabled it will be send later.'
            )
            self.log.exception(msg)

    def put_state(self, uuid: UUID, data: Union[State, LogValue]) -> bool:
        """Make changes to a state."""
        # url=f"/services/2.0/state/{uuid}",
        try:
            return self._no_reply_send(
                data=data,
                url=f"/state/{uuid}",
                method=WappstoMethod.PUT
            )
        except TimeoutError:
            msg = (
                'Error in sending Values.\n'
                'If Offline storage is enabled it will be send later.'
            )
            self.log.exception(msg)

    def get_state(self, uuid: UUID) -> Union[State, None]:
        """Request to get given state data."""
        return self._reply_send(
            data=None,
            url=f"/state/{uuid}",
            method=WappstoMethod.GET
        )

    def delete_state(self, uuid: UUID) -> bool:
        """Remove to given state."""
        # url=f"/services/2.0/state/{uuid}",
        return self._no_reply_send(
            data=None,
            url=f"/state/{uuid}",
            method=WappstoMethod.DELETE
        )
