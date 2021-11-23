import logging
import json
from uuid import UUID

import httpx

from pydantic import parse_obj_as
from pydantic import ValidationError

from typing import Any
from typing import Callable
from typing import Dict
from typing import Union

from ..template import ServiceClass

from ..schema.base_schema import BlobValue
from ..schema.base_schema import Device
from ..schema.base_schema import Network
from ..schema.base_schema import NumberValue
from ..schema.base_schema import State
from ..schema.base_schema import StringValue
from ..schema.base_schema import XmlValue

from ..schema.base_schema import WappstoMetaType
from ..schema.base_schema import WappstoMethods
from ..schema.rest_schema import DeleteList

from ..utils.Exceptions import WappstoError
from ..schema.jsonrpc_schema import StreamEvents

from ..wappsto_ws import WappstoWebSocket


class RestAPI(ServiceClass):

    def __init__(self, token, username, password, url, version="2.0"):
        self.log = logging.getLogger(__name__)
        self.log.addHandler(logging.NullHandler())
        self.base_url = url
        self.update_version(version)

        if token:
            self.login_header = {"X-session": token}
        else:
            if not username or not password:
                msg = "missing required positional argument(s): "
                msg += "'username' " if not username else ""
                msg += "'password' " if not password else ""
                raise TypeError(msg)
            self.session_json = {
                "username": username,
                "password": password,
                "remember_me": True
            }
            self.start_session()
        self.header = {"Accept": "application/json", **self.login_header}

        self.ws = WappstoWebSocket(
            session_id=self.header["X-session"],
            service=url
        )

    def update_version(self, version):
        self.version = version
        _vr = f"/{version}" if version else ""
        self.url = f"https://{self.base_url}/services{_vr}"

    def start_session(self):
        url = f"{self.url}/session"

        rdata = httpx.post(
            url=url,
            headers={"Content-type": "application/json"},
            data=json.dumps(self.session_json)
        )

        if not rdata.ok:
            self._log_request_error(rdata)
            return
        rjson = json.loads(rdata.text)
        self.login_header = {"x-session": rjson["meta"]["id"]}
        return rjson

    def stop_session(self):
        session_uuid = self.login_header.get('X-session')
        url = f"{self.url}/session/{session_uuid}"

        rdata = httpx.delete(
            url=url,
            headers=self.header
        )

        if not rdata.is_error:
            raise WappstoError("Error in Connection.")
        bm_data = parse_obj_as(DeleteList, json.loads(rdata.text))
        return session_uuid in bm_data.deleted

    # #########################################################################
    #                             Helper Functions
    # #########################################################################

    def _constain_check(self, sub: Dict[Any, Any], main: Dict[Any, Any]) -> bool:
        """
        Check the the Sub-dictionary is contained inside the main-dictionary.

        Return True, if all of sub is in the main.
        Return False, if anyting in sub is missing in main.
        """
        return not bool(dict(set(sub.items()) - set(main.items())))

    _stream_event_parser: Dict[StreamEvents, WappstoMethods] = {
        StreamEvents.CREATE: WappstoMethods.POST,
        StreamEvents.UPDATE: WappstoMethods.PUT,
        StreamEvents.DELETE: WappstoMethods.DELETE,
        StreamEvents.DIRECT: ""
    }

    # #########################################################################
    #                               Network API
    # #########################################################################

    def subscribe_network_event(
        self,
        uuid: UUID,
        callback: Callable[[Network, WappstoMethods], None]
    ):
        self.ws.subscribe(
            wappsto_type=WappstoMetaType.network,
            unit_uuid=uuid,
            callback=lambda _id, data: callback(
                data.data,
                self._stream_event_parser.get(data.event)
            )
        )

    def post_network(self, data) -> bool:
        # url=f"/services/2.0/network",
        url = f"{self.url}/network"

        send = data.json()

        rdata = httpx.post(
            url=url,
            headers=self.header,
            data=send
        )

        if not rdata.is_error:
            raise WappstoError("Error in Connection.")
        created = json.loads(rdata.text)

        return self._constain_check(sub=send, main=created)

    def put_network(self, uuid: UUID, data) -> bool:
        if not isinstance(uuid, UUID):
            uuid = UUID(uuid)
        url = f"{self.url}/network/{uuid}"

        send = data.json()

        rdata = httpx.put(
            url=url,
            headers=self.header,
            data=send
        )

        if not rdata.is_error:
            raise WappstoError("Error in Connection.")
        created = json.loads(rdata.text)

        return self._constain_check(sub=send, main=created)

    def get_network(self, uuid: UUID) -> Network:
        if not isinstance(uuid, UUID):
            uuid = UUID(uuid)
        
        url = f"{self.url}/network/{uuid}"

        rdata = httpx.get(
            url=url,
            headers=self.header
        )

        if not rdata.is_error:
            raise WappstoError("Error in Connection.")
        try:
            return parse_obj_as(Network, json.loads(rdata.text))
        except ValidationError:
            raise WappstoError("Network not founded.")

    def delete_network(self, uuid: UUID) -> bool:
        if not isinstance(uuid, UUID):
            uuid = UUID(uuid)
        
        url = f"{self.url}/network/{uuid}"

        rdata = httpx.delete(
            url=url,
            headers=self.header
        )

        if not rdata.is_error:
            raise WappstoError("Error in Connection.")
        bm_data = parse_obj_as(DeleteList, json.loads(rdata.text))
        return uuid in bm_data.deleted

    # #########################################################################
    #                                Device API
    # #########################################################################

    def subscribe_device_event(
        self,
        uuid: UUID,
        callback: Callable[[Device, WappstoMethods], None]
    ):
        self.ws.subscribe(
            wappsto_type=WappstoMetaType.device,
            unit_uuid=uuid,
            callback=lambda _id, data: callback(
                data.data,
                self._stream_event_parser.get(data.event)
            )
        )

    def post_device(self, network_uuid: UUID, data: Device) -> bool:
        # url=f"/services/2.0/network/{uuid}/device",
        url = f"{self.url}/network/{network_uuid}/device"

        send = data.json()

        rdata = httpx.post(
            url=url,
            headers=self.header,
            data=send
        )

        if not rdata.is_error:
            raise WappstoError("Error in Connection.")
        created = json.loads(rdata.text)

        return self._constain_check(sub=send, main=created)

    def put_device(self, uuid: UUID, data: Device) -> bool:
        if not isinstance(uuid, UUID):
            uuid = UUID(uuid)
        url = f"{self.url}/device/{uuid}"

        send = data.json()

        rdata = httpx.put(
            url=url,
            headers=self.header,
            data=send
        )

        if not rdata.is_error:
            raise WappstoError("Error in Connection.")
        created = json.loads(rdata.text)

        return self._constain_check(sub=send, main=created)

    def get_device(self, uuid: UUID) -> Device:
        if not isinstance(uuid, UUID):
            uuid = UUID(uuid)
        
        url = f"{self.url}/device/{uuid}"

        rdata = httpx.get(
            url=url,
            headers=self.header
        )

        if not rdata.is_error:
            raise WappstoError("Error in Connection.")
        try:
            return parse_obj_as(Device, json.loads(rdata.text))
        except ValidationError:
            raise WappstoError("Device not founded.")

    def delete_device(self, uuid: UUID) -> bool:
        if not isinstance(uuid, UUID):
            uuid = UUID(uuid)
        
        url = f"{self.url}/device/{uuid}"

        rdata = httpx.delete(
            url=url,
            headers=self.header
        )

        if not rdata.is_error:
            raise WappstoError("Error in Connection.")
        bm_data = parse_obj_as(DeleteList, json.loads(rdata.text))
        return uuid in bm_data.deleted

    # #########################################################################
    #                                 Value API
    # #########################################################################

    ValueUnion = Union[StringValue, NumberValue, BlobValue, XmlValue]

    def subscribe_value_event(
        self,
        uuid: UUID,
        callback: Callable[[ValueUnion, WappstoMethods], None]
    ):
        self.ws.subscribe(
            wappsto_type=WappstoMetaType.value,
            unit_uuid=uuid,
            callback=lambda _id, data: callback(
                data.data,
                self._stream_event_parser.get(data.event)
            )
        )

    def post_value(self, device_uuid: UUID, data: ValueUnion) -> bool:
        # url=f"/services/2.0/device/{uuid}/value",
        url = f"{self.url}/device/{device_uuid}/value"

        send = data.json()

        rdata = httpx.post(
            url=url,
            headers=self.header,
            data=send
        )

        if not rdata.is_error:
            raise WappstoError("Error in Connection.")
        created = json.loads(rdata.text)

        return self._constain_check(sub=send, main=created)

    def put_value(self, uuid: UUID, data: ValueUnion) -> bool:
        if not isinstance(uuid, UUID):
            uuid = UUID(uuid)
        url = f"{self.url}/value/{uuid}"

        send = data.json()

        rdata = httpx.put(
            url=url,
            headers=self.header,
            data=send
        )

        if not rdata.is_error:
            raise WappstoError("Error in Connection.")
        created = json.loads(rdata.text)

        return self._constain_check(sub=send, main=created)

    def get_value(self, uuid: UUID) -> ValueUnion:
        if not isinstance(uuid, UUID):
            uuid = UUID(uuid)
        
        url = f"{self.url}/value/{uuid}"

        rdata = httpx.get(
            url=url,
            headers=self.header
        )

        if not rdata.is_error:
            raise WappstoError("Error in Connection.")
        try:
            return parse_obj_as(ValueUnion, json.loads(rdata.text))
        except ValidationError:
            raise WappstoError("Value not founded.")

    def delete_value(self, uuid: UUID) -> bool:
        if not isinstance(uuid, UUID):
            uuid = UUID(uuid)
        
        url = f"{self.url}/value/{uuid}"

        rdata = httpx.delete(
            url=url,
            headers=self.header
        )

        if not rdata.is_error:
            raise WappstoError("Error in Connection.")
        bm_data = parse_obj_as(DeleteList, json.loads(rdata.text))
        return uuid in bm_data.deleted

    # #########################################################################
    #                                State API
    # #########################################################################

    def subscribe_state_event(
        self,
        uuid: UUID,
        callback: Callable[[State, WappstoMethods], None]
    ):
        self.ws.subscribe(
            wappsto_type=WappstoMetaType.sate,
            unit_uuid=uuid,
            callback=lambda _id, data: callback(
                data.data,
                self._stream_event_parser.get(data.event)
            )
        )

    def post_state(self, value_uuid: UUID, data: State) -> bool:
        # url=f"/services/2.0/{uuid}/state",
        url = f"{self.url}/value/{value_uuid}/state"

        send = data.json()

        rdata = httpx.post(
            url=url,
            headers=self.header,
            data=send
        )

        if not rdata.is_error:
            raise WappstoError("Error in Connection.")
        created = json.loads(rdata.text)

        return self._constain_check(sub=send, main=created)

    def put_state(self, uuid: UUID, data: State) -> bool:
        if not isinstance(uuid, UUID):
            uuid = UUID(uuid)
        url = f"{self.url}/state/{uuid}"

        send = data.json()

        rdata = httpx.put(
            url=url,
            headers=self.header,
            data=send
        )

        if not rdata.is_error:
            raise WappstoError("Error in Connection.")
        created = json.loads(rdata.text)

        return self._constain_check(sub=send, main=created)

    def get_state(self, uuid: UUID) -> Union[State, None]:
        if not isinstance(uuid, UUID):
            uuid = UUID(uuid)
        
        url = f"{self.url}/state/{uuid}"

        rdata = httpx.get(
            url=url,
            headers=self.header
        )

        if not rdata.is_error:
            raise WappstoError("Error in Connection.")
        try:
            return parse_obj_as(State, json.loads(rdata.text))
        except ValidationError:
            raise WappstoError("state not founded.")

    def delete_state(self, uuid: UUID) -> bool:
        if not isinstance(uuid, UUID):
            uuid = UUID(uuid)
        
        url = f"{self.url}/state/{uuid}"

        rdata = httpx.delete(
            url=url,
            headers=self.header
        )

        if not rdata.is_error:
            raise WappstoError("Error in Connection.")
        bm_data = parse_obj_as(DeleteList, json.loads(rdata.text))
        return uuid in bm_data.deleted
