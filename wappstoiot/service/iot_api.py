import copy
import json
import logging
import re
import threading

from uuid import UUID
from pathlib import Path

from concurrent.futures import ThreadPoolExecutor

from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import slxjsonrpc
from slxjsonrpc.schema.jsonrpc import ErrorModel

from .template import Status
from .template import ServiceClass

from ..schema.base_schema import BlobValue
from ..schema.base_schema import Device
from ..schema.base_schema import Network
from ..schema.base_schema import NumberValue
from ..schema.base_schema import State
from ..schema.base_schema import StringValue
from ..schema.base_schema import XmlValue
from ..schema.base_schema import WappstoObject
from ..schema.base_schema import IdList

from ..schema.iot_schema import JsonData
from ..schema.iot_schema import JsonReply
from ..schema.iot_schema import Success
from ..schema.iot_schema import WappstoMethod
# from ..schema.iot_scgema import WappstoObjectType

from ..utils.certificateread import CertificateRead
from ..utils import observer
from ..utils import tracer

from ..connections.sslsocket import TlsSocket


ValueUnion = Union[StringValue, NumberValue, BlobValue, XmlValue]


# POST   -> onCreate
# GET    -> onRefresh
# PUT    -> onChange
# DELETE -> onDelete

# create  -> POST
# refresh -> GET
# change  -> PUT
# delete  -> DELETE


class IoTAPI(ServiceClass):

    wappstoPort = {
        "dev": 52005,
        "qa": 53005,
        "staging": 54005,
        "prod": 443
    }

    def __init__(self, ca: Path, crt: Path, key: Path, worker_count=2):
        self.log = logging.getLogger(__name__)
        self.log.addHandler(logging.NullHandler())
        self.ca = ca
        self.crt = crt
        self.key = key

        self.timeout = 10

        self.addr, self.port = self._url_gen(self.crt)

        self.connection = TlsSocket(
            address=self.addr,
            port=self.port,
            ca=self.ca,
            crt=self.crt,
            key=self.key,
            observer=observer
        )

        params = {
            x: Union[Success, JsonData] for x in WappstoMethod
        } 

        result = {
            WappstoMethod.GET: JsonReply,
            WappstoMethod.POST: JsonReply,
            WappstoMethod.PUT: JsonReply,
            WappstoMethod.DELETE: JsonReply,
            # WappstoMethod.PATCH: JsonReply,
            # WappstoMethod.HEAD: JsonReply,
        }

        self.subscribers: Dict[
            UUID,
            List[Callable[[WappstoObject, WappstoMethod], None]]
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

        self.killed = threading.Event()
        self.workers = ThreadPoolExecutor(max_workers=worker_count)

        self.workers.submit(self._receive_handler)

    def close(self):
        self.killed.set()
        self.log.debug("Closing Connection.")
        self.connection.close()
        self.log.debug("Closing Workers")
        self.workers.shutdown()
        self.log.debug("IoTAPI Colsed.")

    # #########################################################################
    #                              Helper Methods
    # #########################################################################

    def _url_gen(self, crt):
        cer = CertificateRead(crt=crt)
        port = self.wappstoPort.get(cer.endpoint.split('.')[0], 443)
        if cer.endpoint.split('.')[0] in self.wappstoPort.keys():
            addr = cer.endpoint
        else:
            addr = f"collector.{cer.endpoint}"

        if re.search(r'^[A-Za-z0-9+.-]+://', addr):
            addr = addr.split("://", maxsplit=1)[-1]
        # if not re.search(r':[0-9]+', addr):
        #     addr = f'{addr}:{port}'
        return (addr, port)

    def _receive_handler(self):
        self.log.debug("Receive Handler Started!")
        while not self.killed.is_set():
            try:
                data = self.connection.receive(parser=json.loads)

                if not data:
                    continue

                if not isinstance(data, list):
                    data = [data]
                for elemt in data:
                    _ids = [elemt.get('id', elemt) for elemt in data]
                    self.log.debug(f"Package received: {elemt.get('id', elemt)}")

                trace = tracer.Trace.trace_list_check(
                    jsonrpc_elemts=data,
                    name="Wappsto IoT Receive Thread"
                )

                reply = self.jsonrpc.parser(data)
                self.log.debug(f"Package ID: {_ids}; Reply: {reply}")

                self._send_logic(reply)
                # UNSURE: How do we check if it was send?
                observer.post(Status.SEND, reply)

                self._trace_send_logic(trace, reply)

            except Exception:
                self.log.exception("Receive Handler Error:")
        self.log.debug("Receive Handler Stopped!")

    def _trace_send_logic(self, trace_list, reply_list) -> None:
        if not trace_list:
            return
        for t, d in zip(trace_list, reply_list.__root__):
            if not isinstance(d, ErrorModel):
                t.send_ok(name="Wappsto IoT Receive Thread")
            else:
                t.send_failed(name="Wappsto IoT Receive Thread")

    def _send_logic(self, data, _id=None):
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
                    _id = "; ".join(x.id for x in send_data.__root__)
                elif send_data:
                    _id = send_data.id

                if _id:
                    self.log.debug(f"Package ID: {_id};")

                if send_data:
                    observer.post(Status.SENDING, send_data)
                    self.connection.send(send_data.json(exclude_none=True))

    def _resend_data(self, data):
        # TODO: add the jsonrpc ID to the JsonRpc receive list.
        with self.connection.send_ready:
            self.connection.send(data)

        # j_data = json.loads(data)
        # _cb_event = threading.Event()

        # if j_data.get('params'):
        #     reply = self.jsonrpc.create_request(
        #         callback=lambda data: _cb_event(),
        #         error_callback=lambda err_data: _cb_event(),
        #         method=j_data.get('method'),
        #         params=j_data
        #     )
        # elif j_data.get('result'):
        #     # self.jsonrpc.
        #     pass

        # self._send_logic(reply.json(exclude_none=True))

        # self.log.debug(f"--CALLBACK Ready! {rpc_id}")
        # if _cb_event.wait(timeout=self.timeout):
        #     if _data:
        #         self.log.debug(f"--CALLBACK EVENT! {rpc_id}")
        #         observer.post(Status.SEND, rpc_data)
        #         return _data.value
        #     if _err_data:
        #         self.log.warning(f"--CALLBACK Error! {_err_data}")
        #         # raise ConnectionError(_err_data.message)
        # self.log.debug(f"--CALLBACK None! {rpc_id}")
        # observer.post(Status.SENDERROR, rpc_data)
        # return None

    # -------------------------------------------------------------------------
    #                               API Helpers
    # -------------------------------------------------------------------------

    def _no_reply_send(self, data, url, method) -> bool:
        j_data = JsonData(
            data=data,
            url=url
        )

        self.log.debug(f"Sending for: {url}")

        _cb_event = threading.Event()
        _err_data: Optional[ErrorModel] = None

        def _err_callback(err_data: ErrorModel):
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
                # raise ConnectionError(_err_data.message)
            self.log.debug(f"--CALLBACK EVENT! {rpc_id}")
            observer.post(Status.SEND, rpc_data)
            return True
        observer.post(Status.SENDERROR, rpc_data)
        self.log.debug(f"--CALLBACK None! {rpc_id}")
        return False

    def _reply_send(
        self,
        data,
        url,
        method
    ) -> Optional[Union[Device, Network, ValueUnion, State, IdList]]:
        j_data = JsonData(
            data=data,
            url=url
        )

        self.log.debug(f"Sending for: {url}")

        _cb_event = threading.Event()
        _err_data: ErrorModel = None

        def _err_callback(err_data: ErrorModel):
            nonlocal _err_data
            nonlocal _cb_event
            _err_data = err_data
            _cb_event.set()

        _data: Optional[JsonReply] = None

        def _data_callback(data: JsonReply):
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
                observer.post(Status.SEND, rpc_data)
                return _data.value
            if _err_data:
                self.log.warning(f"--CALLBACK Error! {_err_data}")
                # raise ConnectionError(_err_data.message)
        self.log.debug(f"--CALLBACK None! {rpc_id}")
        observer.post(Status.SENDERROR, rpc_data)
        return None

    # -------------------------------------------------------------------------
    #                              Callback Helpers
    # -------------------------------------------------------------------------

    def _cb_handler(self, data: JsonData, method: WappstoMethod):
        object_uuid = UUID(data.url.split("/")[-1])
        self.log.debug(f"Object UUID: {object_uuid}")
        for cb in self.subscribers.get(object_uuid, [self._default_cb]):
            self.workers.submit(cb, data.data, method)
            self.log.debug(f"Submitted to Worker: {cb}")

    def _default_cb(self, data: WappstoObject, method: WappstoMethod):
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
    #                               Network API
    # #########################################################################

    def subscribe_network_event(
        self,
        uuid: UUID,
        callback: Callable[[Network, WappstoMethod], None]
    ):
        self.subscribers.setdefault(uuid, []).append(callback)

    def post_network(self, data: Network) -> bool:
        # url=f"/services/2.0/network",
        return self._no_reply_send(
            data=data,
            url="/network/",
            method=WappstoMethod.POST
        )

    def put_network(self, uuid: UUID, data: Network) -> bool:
        # url=f"/services/2.0/network/{uuid}",
        return self._no_reply_send(
            data=data,
            url=f"/network/{uuid}",
            method=WappstoMethod.PUT
        )

    def get_network(self, uuid: UUID) -> Optional[Network]:
        # url=f"/services/2.0/network/{uuid}",
        return self._reply_send(
            data=None,  # NOTE: Should be nonexistent or Null.
            url=f"/network/{uuid}",
            method=WappstoMethod.GET
        )

    def delete_network(self, uuid: UUID) -> bool:
        # url=f"/services/2.0/network/{uuid}",
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
    ):
        self.subscribers.setdefault(uuid, []).append(callback)

    def post_device(self, network_uuid: UUID, data: Device) -> bool:
        # url=f"/services/2.0/{uuid}/device",
        return self._no_reply_send(
            data=data,
            url=f"/network/{network_uuid}/device/",
            method=WappstoMethod.POST
        )

    def put_device(self, uuid: UUID, data: Device) -> bool:
        # url=f"/services/2.0/device/{uuid}",
        return self._no_reply_send(
            data=data,
            url=f"/device/{uuid}",
            method=WappstoMethod.PUT
        )

    def get_device_where(self, network_uuid: UUID, **kwargs: Dict[str, str]) -> List[UUID]:
        # /network/{uuid}/device?this_name==X
        key, value = list(kwargs.items())[0]
        self.log.debug(f"{locals()}")
        url = f"/network/{network_uuid}/device?this_{key}=={value}"
        data: IdList = self._reply_send(
            data=None,
            url=url,
            method=WappstoMethod.GET
        )

        return getattr(data, "id", None)

    def get_device(self, uuid: UUID) -> Union[Device, None]:
        # url=f"/services/2.0/device/{uuid}",
        return self._reply_send(
            data=None,
            url=f"/device/{uuid}",
            method=WappstoMethod.GET
        )

    def delete_device(self, uuid: UUID) -> bool:
        # url=f"/services/2.0/device/{uuid}",
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
    ):
        self.subscribers.setdefault(uuid, []).append(callback)

    def post_value(self, device_uuid: UUID, data: ValueUnion) -> bool:
        # url=f"/services/2.0/{uuid}/value",
        return self._no_reply_send(
            data=data,
            url=f"/device/{device_uuid}/value/",
            method=WappstoMethod.POST
        )

    def put_value(self, uuid: UUID, data: ValueUnion) -> bool:
        # url=f"/services/2.0/value/{uuid}",
        return self._no_reply_send(
            data=data,
            url=f"/value/{uuid}",
            method=WappstoMethod.PUT
        )

    def get_value_where(self, device_uuid: UUID, **kwargs: Dict[str, str]) -> List[UUID]:
        # /network/{uuid}/device?this_name==X
        key, value = list(kwargs.items())[0]
        url = f"/device/{device_uuid}/value?this_{key}=={value}"
        data: IdList = self._reply_send(
            data=None,
            url=url,
            method=WappstoMethod.GET
        )

        return getattr(data, "id", None)

    def get_value(self, uuid: UUID) -> Union[ValueUnion, None]:
        # url=f"/services/2.0/value/{uuid}",
        return self._reply_send(
            data=None,
            url=f"/value/{uuid}",
            method=WappstoMethod.GET
        )

    def delete_value(self, uuid: UUID) -> bool:
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
    ):
        self.subscribers.setdefault(uuid, []).append(callback)

    def post_state(self, value_uuid: UUID, data: State) -> bool:
        # url=f"/services/2.0/{uuid}/state",
        return self._no_reply_send(
            data=data,
            url=f"/value/{value_uuid}/state/",
            method=WappstoMethod.POST
        )

    def put_state(self, uuid: UUID, data: State) -> bool:
        # url=f"/services/2.0/state/{uuid}",
        return self._no_reply_send(
            data=data,
            url=f"/state/{uuid}",
            method=WappstoMethod.PUT
        )

    def get_state(self, uuid: UUID) -> Union[State, None]:
        return self._reply_send(
            data=None,
            url=f"/state/{uuid}",
            method=WappstoMethod.GET
        )

    def delete_state(self, uuid: UUID) -> bool:
        # url=f"/services/2.0/state/{uuid}",
        return self._no_reply_send(
            data=None,
            url=f"/state/{uuid}",
            method=WappstoMethod.DELETE
        )
