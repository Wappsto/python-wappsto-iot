import itertools
import json
import socket
import threading
import time
import traceback
import uuid


from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from pydantic import BaseModel
from pydantic import Field

from utils import pkg_smithing


class ErrorException(Exception):
    def __init__(self, code, msg, data):
        self.code = code
        self.msg = msg
        self.data = data


class ObjectModel(BaseModel):
    object_type: str
    self_uuid: Optional[uuid.UUID]
    name: Optional[str]
    extra_info: dict = Field(default_factory=dict)
    children: List[uuid.UUID] = Field(default_factory=list)
    parent: Optional[uuid.UUID] = None


class UrlObject(BaseModel):
    object_type: str
    self_uuid: Optional[uuid.UUID]
    parent: Optional[uuid.UUID]


class Parameters(BaseModel):
    left: str
    op: Optional[str]
    right: Optional[str]


def pairwise(iterable):
    """
    Pair the iterables, in groups of 2.

    s -> (s0, s1), (s2, s3), (s4, s5), ...

    Taking advantage of the iter structure and zip's use of iters.

    Args:
        iterable: The list to be paired
    """
    a = iter(iterable)
    return itertools.zip_longest(a, a)


class SimuServer(object):

    param_op_list: List[str] = [
        '==', '>=', '<=', '!=', '=', '<', '>'
    ]

    def __init__(
        self,
        network_uuid: uuid.UUID,
        name: str,
        description: Optional[str] = None
    ):
        self.network_uuid: uuid.UUID = network_uuid
        self.objects: Dict[uuid.UUID, ObjectModel] = {}
        self.objects[self.network_uuid] = ObjectModel(
            object_type='network',
            self_uuid=self.network_uuid,
            # children=[],
            name=name,
            extra_info={'description': description} if description else {}
        )

        self.failed_data: List[Tuple[bool, str]] = []
        self.killed = threading.Event()
        self.data_in: List[bytes] = []

    def add_object(
        self,
        this_uuid: uuid.UUID,
        this_type: str,
        parent_uuid: Optional[uuid.UUID],
        this_name: Optional[str],
        children: Optional[List] = None,
        extra_info: Optional[dict] = None
    ):
        if parent_uuid not in self.objects and this_type != 'network':
            raise ValueError("Parent need to exist!")
        self.objects[this_uuid] = ObjectModel(
            parent=parent_uuid,
            object_type=this_type,
            self_uuid=this_uuid,
            name=this_name,
            children=children if children else [],
            extra_info=extra_info if extra_info else {}
        )
        if this_type != 'network':
            if not parent_uuid:
                raise ValueError("Parent UUID are needed!")
            self.objects[parent_uuid].children.append(this_uuid)

    def _add_object_from_dict(
        self,
        parent_uuid: uuid.UUID,
        self_type: str,
        data: dict
    ) -> uuid.UUID:
        this_uuid: uuid.UUID = uuid.UUID(data['meta']['id'])
        this_type = data['meta'].get('type') if self_type != "state" else "state"

        children: List = []
        this_name: Optional[str] = None

        if this_type:
            msg = f"ADD: Conflict in type: {this_type} == {self_type}, for: {this_uuid}"
            self.add_check(this_type == self_type, msg)

        if self_type == 'value':
            this_name = data.pop('name')
            children = data.pop('state') if 'state' in data.keys() else []
        elif self_type == 'device':
            this_name = data.pop('name')
            children = data.pop('value') if 'value' in data.keys() else []
        elif self_type == 'network':
            this_name = data.pop('name')
            children = data.pop('device') if 'device' in data.keys() else []
        elif self_type == 'state':
            pass

        data.pop('meta')

        self.add_object(
            this_uuid=this_uuid,
            this_type=this_type,
            parent_uuid=parent_uuid,
            this_name=this_name,
            children=children,
            extra_info=data
        )
        return this_uuid

    def _update_object_from_dict(
        self,
        self_type: str,
        data: dict
    ) -> uuid.UUID:
        this_uuid: uuid.UUID = uuid.UUID(data['meta']['id'])
        this_type = data['meta'].get('type') if self_type != "state" else "state"

        children: List = []
        this_name: Optional[str] = None

        if this_type:
            msg = f"UPDATE: Conflict in type: {this_type} == {self_type}, for: {this_uuid}"
            self.add_check(this_type == self_type, msg)

        if self_type == 'value':
            this_name = data.pop('name')
            children = data.pop('state') if 'state' in data.keys() else []
        elif self_type == 'device':
            this_name = data.pop('name')
            children = data.pop('value') if 'value' in data.keys() else []
        elif self_type == 'network':
            this_name = data.pop('name')
            children = data.pop('device') if 'device' in data.keys() else []
        elif self_type == 'state':
            pass

        data.pop('meta')

        old_data = self.objects[this_uuid]

        self.add_object(
            this_uuid=this_uuid,
            this_type=this_type,
            parent_uuid=old_data.parent,
            this_name=this_name if this_name else old_data.name,
            children=children if children else old_data.children,
            extra_info=old_data.extra_info.update(data)
        )
        return this_uuid

    def add_check(self, result, text):
        self.failed_data.append((result, text))

    def fail_check(self):
        for test, text in self.failed_data:
            assert test, text

    def get_socket(
        self,
        mock_rw_socket,
        mock_ssl_socket
    ):
        self.killed.clear()

        mock_ssl_socket.return_value.close.side_effect = lambda: self.killed.set()

        def socket_simu(*args, **kwargs) -> bytes:
            timeout = 0
            if mock_rw_socket.return_value.settimeout.call_args:
                t_data, _ = mock_rw_socket.return_value.settimeout.call_args
                timeout = t_data[0] + time.perf_counter()
            while not self.killed.is_set():
                if timeout <= time.perf_counter():
                    break

                if not mock_ssl_socket.return_value.sendall.call_args:
                    time.sleep(0.01)
                    continue
                temp_data, _ = mock_ssl_socket.return_value.sendall.call_args
                send_data = temp_data[0]
                mock_ssl_socket.return_value.sendall.call_args = None

                data = None
                try:
                    self.data_in.append(send_data)
                    data = self.rpc_handle(send_data)
                except Exception as error:
                    self.add_check(
                        False,
                        f"send_data={send_data}\n{error}\n{traceback.format_exc()}"
                    )
                    raise error
                else:
                    return data

            time.sleep(0.5)
            raise socket.timeout(timeout)

        mock_ssl_socket.return_value.recv.side_effect = socket_simu

    def _params_parser(self, params) -> List[Parameters]:
        param_list: List[Parameters] = []

        for parameters in params.split('&'):
            for op in self.param_op_list:
                if op in parameters:
                    temp = parameters.split(op)
                    param_list.append(
                        Parameters(
                            left=temp[0],
                            op=op,
                            right=temp[-1],
                        )
                    )
                    break
            else:
                param_list.append(
                    Parameters(
                        left=parameters,
                    )
                )

        return param_list

    def _objectmodel_parser(self, path) -> UrlObject:
        # NOTE: Tested with:
        # /network/xxxxxxxx-xxxx-4xxx-axxx-xxxxxxxxxxxx/device/xxxxxxxx-xxxx-4xxx-axxx-xxxxxxxxxxxx/value/xxxxxxxx-xxxx-4xxx-axxx-xxxxxxxxxxxx/state/xxxxxxxx-xxxx-4xxx-axxx-xxxxxxxxxxxx
        # /network/xxxxxxxx-xxxx-4xxx-axxx-xxxxxxxxxxxx/device
        # /device/xxxxxxxx-xxxx-4xxx-axxx-xxxxxxxxxxxx
        # /network/
        parent_uuid: Optional[uuid.UUID] = None
        object_type: Optional[str] = None
        object_uuid: Optional[uuid.UUID] = None

        for obj_type, obj_uuid in pairwise(path.split('/')[1:]):
            parent_uuid = object_uuid
            object_type = obj_type
            object_uuid = obj_uuid if obj_uuid else None

        return UrlObject(
            object_type=object_type,
            self_uuid=object_uuid,
            parent=parent_uuid,
        )

    def _url_parser(self, url) -> Tuple[UrlObject, List[Parameters]]:
        params = url.split('?')
        param_list: List[Parameters] = self._params_parser(params[-1]) if len(params) > 1 else []
        obj: UrlObject = self._objectmodel_parser(url.split('?')[0])

        return (
            obj,
            param_list
        )

    def rpc_handle(self, data: bytes) -> bytes:
        j_data = json.loads(data.decode())
        # TODO: check if it is a list!!!!!!
        pkg_id = j_data['id']

        error = j_data.get('error')
        if error:
            self.add_check(False, error)
            return json.dumps(
                pkg_smithing.rpc_pkg(
                    pkg_id=pkg_id,
                    pkg_data=True
                )
            ).encode()

        pkg_method = j_data['method']
        the_url = j_data['params']['url']
        the_data = j_data['params'].get('data')
        fast_send = j_data['params'].get('meta', {}).get('fast', False)
        # identifier = j_data['params']['meta']['identifier']

        url_obj: Tuple[UrlObject, List[Parameters]] = self._url_parser(the_url)

        # TODO: Handle a error as received data!!

        try:

            if pkg_method.upper() == 'GET':
                r_data = self.get_handle(
                    data=the_data,
                    fast_send=fast_send,
                    url_obj=url_obj
                )
            elif pkg_method.upper() == 'POST':
                r_data = self.post_handle(
                    data=the_data,
                    fast_send=fast_send,
                    url_obj=url_obj
                )
            elif pkg_method.upper() == 'PUT':
                r_data = self.put_handle(
                    data=the_data,
                    fast_send=fast_send,
                    url_obj=url_obj
                )
            elif pkg_method.upper() == 'DELETE':
                r_data = self.delete_handle(
                    data=the_data,
                    fast_send=fast_send,
                    url_obj=url_obj
                )
            else:
                self.add_check(False, f"Unknown method: {pkg_method}")
                return pkg_smithing.error_pkg(
                    pkg_id=pkg_id,
                    data=j_data,
                    code=-32601,
                    msg="Unhandled Method",
                )

        except ErrorException as err:
            self.add_check(False, f"Could not parse data: {data!r}")
            return json.dumps(
                pkg_smithing.error_pkg(
                    pkg_id=pkg_id,
                    code=err.code,
                    msg=err.msg,
                    data=err.data
                )
            ).encode()

        return json.dumps(
            pkg_smithing.rpc_pkg(
                pkg_id=pkg_id,
                pkg_data=r_data
            )
        ).encode()

    def get_handle(
        self,
        data: dict,
        url_obj: Tuple[UrlObject, List[Parameters]],
        fast_send=False
    ) -> Union[dict, bool]:

        the_uuid = url_obj[0].self_uuid
        the_type = url_obj[0].object_type

        if url_obj[1] or not the_uuid:
            return self._search_obj(data=data, url_obj=url_obj)

        if the_type == "network":
            the_uuid = self.network_uuid

        if the_uuid not in self.objects.keys():
            self.add_check(False, f"GET: {the_uuid} not found.")
            raise ErrorException(
                code=-32602,
                msg="UUID not found!",
                data=str(the_uuid)
            )

        return self._obj_generate(obj_uuid=the_uuid)

    def post_handle(
        self,
        data: dict,
        url_obj: Tuple[UrlObject, List[Parameters]],
        fast_send=False
    ) -> Union[dict, bool]:

        parent_uuid = url_obj[0].parent
        the_type = url_obj[0].object_type

        if the_type == "network":
            new_unit_uuid = self._update_object_from_dict(
                self_type=the_type,
                data=data,
            )
        elif parent_uuid not in self.objects.keys():
            self.add_check(False, f"POST: {parent_uuid}/{the_type} not found.")
            raise ErrorException(
                code=-32602,
                msg="UUID not found!",
                data=str(parent_uuid)
            )
        elif parent_uuid is not None:
            new_unit_uuid = self._add_object_from_dict(
                parent_uuid=parent_uuid,
                self_type=the_type,
                data=data,
            )

        if fast_send:
            return True

        return self._obj_generate(obj_uuid=new_unit_uuid)

    def put_handle(
        self,
        data: dict,
        url_obj: Tuple[UrlObject, List[Parameters]],
        fast_send=False
    ) -> Union[dict, bool]:

        the_uuid = url_obj[0].self_uuid

        if the_uuid not in self.objects.keys() or not the_uuid:
            self.add_check(False, f"GET: {the_uuid} not found.")
            raise ErrorException(
                code=-32602,
                msg="UUID not found!",
                data=str(the_uuid)
            )

        self._update_object_from_dict(
            self_type=url_obj[0].object_type,
            data=data
        )

        if fast_send:
            return True

        return self._obj_generate(obj_uuid=the_uuid)

    def delete_handle(
        self,
        data: dict,
        url_obj: Tuple[UrlObject, List[Parameters]],
        fast_send=False
    ) -> Union[dict, bool]:

        the_uuid = url_obj[0].self_uuid

        if the_uuid not in self.objects.keys() or not the_uuid:
            self.add_check(False, f"GET: {the_uuid} not found.")
            raise ErrorException(
                code=-32602,
                msg="UUID not found!",
                data=str(the_uuid)
            )

        the_obj = self._obj_generate(obj_uuid=the_uuid)

        del self.objects[the_uuid]

        if fast_send:
            return True

        return the_obj

    def _search_obj(
        self,
        data: dict,
        url_obj: Tuple[UrlObject, List[Parameters]]
    ) -> dict:
        parent = url_obj[0].parent
        obj_type = url_obj[0].object_type
        if parent not in self.objects.keys():
            # UNSURE: Should it raise an ErrorException instead?
            self.add_check(False, f"Search: {parent} not found.")
            return pkg_smithing.idlist_pkg(
                obj_type=obj_type
            )

        if not parent:
            children = [self.network_uuid]
        else:
            children = self.objects[parent].children

        valid_children: List[uuid.UUID] = []

        for param in url_obj[1]:
            key = param.left.replace("this_", "")
            for child in children:
                if param.op == "==":
                    if self.objects[child].dict()[key] == param.right:
                        valid_children.append(child)
                elif param.op == "!=":
                    if self.objects[child].dict()[key] != param.right:
                        valid_children.append(child)
                # NOTE: We should not need more it this system test.

        return pkg_smithing.idlist_pkg(
            obj_type=obj_type,
            obj_list=valid_children
        )

    def _obj_generate(self, obj_uuid: uuid.UUID) -> dict:
        obj_data = self.objects[obj_uuid]
        # NOTE: Can be make to a dictionary instead!
        if obj_data.object_type == 'network':
            return pkg_smithing.network_pkg(
                obj_uuid=obj_data.self_uuid,
                obj_children=obj_data.children,
                name=obj_data.name,
                **obj_data.extra_info
            )
        elif obj_data.object_type == 'device':
            return pkg_smithing.device_pkg(
                obj_uuid=obj_data.self_uuid,
                obj_children=obj_data.children,
                name=obj_data.name,
                **obj_data.extra_info
            )
        elif obj_data.object_type == 'value':
            return pkg_smithing.value_pkg(
                obj_uuid=obj_data.self_uuid,
                obj_children=obj_data.children,
                name=obj_data.name,
                **obj_data.extra_info
            )
        elif obj_data.object_type == 'state':
            return pkg_smithing.state_pkg(
                obj_uuid=obj_data.self_uuid,
                **obj_data.extra_info
            )
        else:
            raise ErrorException(
                code=-32602,
                msg="Unknown Object type!",
                data=obj_data.object_type
            )
