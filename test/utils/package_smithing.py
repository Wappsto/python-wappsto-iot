import datetime
import json
import random
import socket
import string
import threading
import time
import traceback
import uuid

from typing import Callable
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from rich import traceback as rich_traceback


rich_traceback.install(show_locals=True)


killed = threading.Event()

failed_data: List[Tuple[bool, str]] = []


class continue_raise(Exception):
    pass


class break_raise(Exception):
    pass


class done_raise(Exception):
    pass


def add_check(result, text):
    failed_data.append((result, text))


def fail_check():
    global failed_data
    for test, text in failed_data:
        assert test, text


def socket_generator(
    mock_rw_socket,
    mock_ssl_socket,
    cycle_list: List[Callable[[bytes], bytes]]
):

    def socket_simu(*args, **kwargs) -> bytes:
        global killed
        timeout = 0
        if mock_rw_socket.return_value.settimeout.call_args:
            t_data, _ = mock_rw_socket.return_value.settimeout.call_args
            timeout = t_data[0] + time.perf_counter()
        while not killed.is_set():
            if timeout <= time.perf_counter():
                break

            if not mock_ssl_socket.return_value.sendall.call_args:
                time.sleep(0.01)
                continue
            temp_data, _ = mock_ssl_socket.return_value.sendall.call_args
            send_data = temp_data[0]
            mock_ssl_socket.return_value.sendall.call_args = None

            if not cycle_list:
                add_check(False, f"unexpected data: {send_data}")
                time.sleep(0.01)
                continue

            data = None
            try:
                data = cycle_list[0](send_data)
            except continue_raise:
                continue
            except break_raise:
                break
            except done_raise:
                if data:
                    del cycle_list[0]
                # UNSURE: How can there bee chained cycle_list from other functions?
            except Exception as error:
                add_check(False, f"{error}\n{traceback.format_exc()}")
                raise error
            else:
                if data:
                    del cycle_list[0]
                return data

        time.sleep(0.5)
        raise socket.timeout(timeout)

    mock_ssl_socket.return_value.recv.side_effect = socket_simu


def convert_timestamp(timestamp: Optional[datetime.datetime] = None) -> str:
    """
    Return The default timestamp used for Wappsto.

    The timestamp are always set to the UTC timezone.

    Returns:
        The UTC time string in ISO format.
    """
    if not timestamp:
        return datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    return timestamp.strftime('%Y-%m-%dT%H:%M:%S.%fZ')


def get_success_pkg(pkg_id: str, timestamp: Optional[datetime.datetime] = None) -> bytes:
    pkg_success = {
        "jsonrpc": "2.0",
        "id": pkg_id,
        "result": {
            "value": True,
            "meta": {
                "server_send_time": convert_timestamp(timestamp)
            }
        }
    }

    return json.dumps(pkg_success).encode()


def get_empty_network(
    pkg_id: str,
    network_uuid: Union[str, uuid.UUID],
    timestamp: Optional[datetime.datetime] = None,
    network_name: Optional[str] = None
) -> bytes:
    if not network_name:
        network_name = "".join(
            random.choices(string.ascii_letters + string.digits, k=10)
        )

    empty_network = {
        "jsonrpc": "2.0",
        "id": pkg_id,
        "result": {
            'value': {
                'device': [],
                'name': network_name,
                'description': '',
                'meta': {
                    'id': str(network_uuid),
                    'type': 'network',
                    'version': '2.0'
                }
            },
            "meta": {
                "server_send_time": convert_timestamp(timestamp)
            }
        }
    }

    return json.dumps(empty_network).encode()


def get_device_pkg(
    pkg_id: str,
    device_uuid: Union[uuid.UUID],
    device_name: Optional[str] = None,
    value_list: Optional[List[uuid.UUID]] = None,
    timestamp: Optional[datetime.datetime] = None,
):
    value_str_list: List[str] = []
    if value_list:
        value_str_list = [str(x) for x in value_list]

    get_device = {
        "jsonrpc": "2.0",
        "id": pkg_id,
        "result": {
            "value": {
                "status": [],
                "value": value_str_list,
                "name": device_name,
                "meta": {
                    "id": str(device_uuid),
                    "type": "device",
                    "version": "2.0"
                }
            },
            "meta": {
                "server_send_time": convert_timestamp(timestamp)
            }
        }
    }
    return json.dumps(get_device).encode()


def get_value_pkg(
    pkg_id: str,
    value_type,
    permission,
    value_uuid: Union[uuid.UUID],
    value_name: Optional[str] = None,
    state_list: Optional[List[uuid.UUID]] = None,
    timestamp: Optional[datetime.datetime] = None,
):
    from wappstoiot.modules.template import valueSettings
    value_s = valueSettings[value_type]

    state_str_list: List[str] = []
    if state_list:
        state_str_list = [str(x) for x in state_list]

    get_value = {
        "jsonrpc": "2.0",
        "id": pkg_id,
        "result": {
            "value": {
                "state": state_str_list,
                "name": value_name,
                "type": value_type.value,
                "permission": permission.value,
                "number": {
                    "min": value_s.min,
                    "max": value_s.max,
                    "step": value_s.step
                },
                "meta": {
                    "id": str(value_uuid),
                    "type": "value",
                    "version": "2.0"
                }
            },
            "meta": {
                "server_send_time": convert_timestamp(timestamp)
            }
        }
    }
    return json.dumps(get_value).encode()


def get_idlist(
    pkg_id: str,
    timestamp: Optional[datetime.datetime] = None,
    device_list: Optional[List[uuid.UUID]] = None
):
    device_str_list: List[str] = []
    if device_list:
        device_str_list = [str(x) for x in device_list]

    empty_idlist = {
        "jsonrpc": "2.0",
        "id": pkg_id,
        "result": {
            "value": {
                "child": [{"type": "device", "version": "2.0"}] if device_str_list else [],
                "id": device_str_list,
                "more": False,
                "limit": 1000,
                "count": len(device_str_list),
                "meta": {
                    "type": "idlist",
                    "version": "2.0"
                }
            },
            "meta": {
                "server_send_time": convert_timestamp(timestamp)
            }
        }
    }
    return json.dumps(empty_idlist).encode()


def get_network_create_cycle(
    network_uuid: uuid.UUID,
    changed: bool,
    network_name: str = ""
) -> List[Callable[[bytes], bytes]]:
    cycle_list: List[Callable[[bytes], bytes]] = []

    def get_network_reply(data: bytes) -> bytes:
        j_data = json.loads(data.decode())
        the_id = j_data['id']
        the_method = j_data['method']
        the_url = j_data['params']['url']
        if the_method.upper() != 'GET':
            add_check(False, f"GET network request: {the_method.upper()} == 'GET'")
            raise continue_raise

        if not the_url.split("/")[-1] == str(network_uuid):
            add_check(False, f"GET network request: {the_url.split('/')[-1]} == '{str(network_uuid)}'")
            raise continue_raise

        return get_empty_network(
            pkg_id=the_id,
            network_uuid=network_uuid,
            network_name=network_name,
        )

    cycle_list.append(get_network_reply)

    def post_network_reply(data: bytes) -> bytes:
        j_data = json.loads(data.decode())
        the_id = j_data['id']
        network_id = j_data['params']['data']['meta']['id']
        network_n = j_data['params']['data']['name']
        the_method = j_data['method']

        if the_method.upper() != 'POST':
            raise continue_raise

        if not changed:
            add_check(False, "Should only receive a post if something changed.")
            raise continue_raise

        if network_id != str(network_uuid):
            add_check(False, f"POST network request: {network_id} == '{str(network_uuid)}'")
            raise continue_raise

        if network_name and network_n != network_name:
            add_check(False, f"POST network request: {network_n} == '{network_name}'")

        return get_success_pkg(pkg_id=the_id)
    cycle_list.append(post_network_reply)

    return cycle_list


def get_device_create_cycle(
    network_uuid: uuid.UUID,
    empty: bool,
    changed: bool,
    device_uuid: Optional[uuid.UUID] = None,
    device_name: Optional[str] = None,
    value_list: Optional[List[uuid.UUID]] = None,
):
    cycle_list: List[Callable[[bytes], bytes]] = []

    def get_device_by_name(data: bytes) -> bytes:  # TODO: !!
        j_data = json.loads(data.decode())
        the_id = j_data['id']
        the_method = j_data['method']
        the_url = j_data['params']['url']
        if the_method.upper() != 'GET':
            add_check(False, f"GET device request: {the_method.upper()} == 'GET'")
            raise continue_raise

        if the_url.split("/")[2] != str(network_uuid):
            add_check(False, f"GET device request: {the_url.split('/')[2]} == '{str(network_uuid)}'")
            raise continue_raise

        if empty and not device_uuid:
            return get_idlist(
                pkg_id=the_id,
                device_list=[device_uuid] if device_uuid else None,
            )

        if the_url.split("==")[-1] != device_name:
            add_check(False, f"GET device request: {the_url.split('==')[-1]} == '{device_name}'")
            raise continue_raise

        return get_idlist(  # UNSURE: the Device object or a idList with the UUID in it?
            pkg_id=the_id,
            device_list=[device_uuid] if device_uuid else None
        )
    cycle_list.append(get_device_by_name)

    def get_device(data: bytes) -> bytes:
        j_data = json.loads(data.decode())
        the_id = j_data['id']
        the_method = j_data['method']
        the_url = j_data['params']['url']
        if the_method.upper() != 'GET':
            add_check(False, f"GET device request: {the_method.upper()} == 'GET'")
            raise continue_raise

        if the_url.split("/")[-1] != str(device_uuid):
            add_check(False, f"GET device request: {the_url.split('/')[-1]} == {device_uuid}")
            raise continue_raise

        return get_device_pkg(
            pkg_id=the_id,
            device_uuid=device_uuid,
            device_name=device_name,
            value_list=value_list
        )

    if empty:
        cycle_list.append(get_device)

    def post_device(data: bytes) -> bytes:
        j_data = json.loads(data.decode())
        the_id = j_data['id']
        device_id = j_data['params']['data']['meta']['id']
        device_n = j_data['params']['data']['name']
        the_method = j_data['method']

        if the_method.upper() != 'POST':
            raise continue_raise

        if device_id != str(device_uuid):
            add_check(False, f"POST device request: {device_id} == '{str(device_uuid)}'")
            raise continue_raise

        if device_name and device_n != device_name:
            add_check(False, f"POST device request: {device_n} == '{device_name}'")
            raise continue_raise

        return get_success_pkg(pkg_id=the_id)
    if not empty:  # or changed!
        cycle_list.append(post_device)

    return cycle_list


def get_value_create_cycle(
    device_uuid: uuid.UUID,
    empty: bool,
    changed: bool,
    value_type,
    permission,
    state_list: Optional[List[uuid.UUID]] = None,
    value_uuid: Optional[uuid.UUID] = None,
    value_name: Optional[str] = None,
):
    cycle_list: List[Callable[[bytes], bytes]] = []

    def get_value_by_name(data: bytes) -> bytes:  # TODO: !!
        j_data = json.loads(data.decode())
        the_id = j_data['id']
        the_method = j_data['method']
        the_url = j_data['params']['url']
        if the_method.upper() != 'GET':
            add_check(False, f"GET device request: {the_method.upper()} == 'GET'")
            raise continue_raise

        if the_url.split("/")[2] != str(device_uuid):
            add_check(False, f"GET device request: {the_url.split('/')[2]} == '{str(device_uuid)}'")
            raise continue_raise

        if empty and not value_uuid:
            return get_idlist(
                pkg_id=the_id,
                device_list=[value_uuid] if value_uuid else None,
            )

        if the_url.split("==")[-1] != value_name:
            add_check(False, f"GET device request: {the_url.split('==')[-1]} == '{value_name}'")
            raise continue_raise

        return get_idlist(  # UNSURE: the Device object or a idList with the UUID in it?
            pkg_id=the_id,
            device_list=[value_uuid] if value_uuid else None
        )
    cycle_list.append(get_value_by_name)

    def get_value(data: bytes) -> bytes:
        j_data = json.loads(data.decode())
        the_id = j_data['id']
        the_method = j_data['method']
        the_url = j_data['params']['url']
        if the_method.upper() != 'GET':
            add_check(False, f"GET device request: {the_method.upper()} == 'GET'")
            raise continue_raise

        if the_url.split("/")[-1] != str(value_uuid):
            add_check(False, f"GET device request: {the_url.split('/')[-1]} == {value_uuid}")
            raise continue_raise

        return get_value_pkg(
            pkg_id=the_id,
            value_type=value_type,
            value_uuid=value_uuid,
            permission=permission,
            value_name=value_name,
            state_list=state_list
        )
    if empty:
        cycle_list.append(get_value)

    return cycle_list
