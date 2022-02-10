import datetime
import json
import random
import socket
import string
import threading
import time
import uuid

from typing import Callable
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union


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
        the_method = j_data['method']

        if the_method.upper() != 'POST':
            raise continue_raise

        if not changed:
            add_check(False, "Should only receive a post if something changed.")
            raise continue_raise

        if network_id != str(network_uuid):
            add_check(False, f"POST network request: {network_id} == '{str(network_uuid)}'")
            raise continue_raise

        if network_name:
            # assert j_data['params']['data']['name'] == str(network_name)
            add_check(False, f"POST network request: {j_data['params']['data']['name']} == '{network_name}'")

        return get_success_pkg(pkg_id=the_id)
    cycle_list.append(post_network_reply)

    return cycle_list
