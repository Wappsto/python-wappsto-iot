"""This the the Simple Wappsto Python user-interface to the Wappsto devices."""

# #############################################################################
#                             Modules Import Stuff
# #############################################################################


import __main__
import atexit
import json
import logging
import threading
import uuid

from pathlib import Path
from enum import Enum


from typing import Any, Dict, Optional, Union, Callable, cast


from .modules.network import Network
# from .modules.network import ConnectionStatus
# from .modules.network import ConnectionTypes
# from .modules.network import NetworkChangeType  # NOt needed anymore.
# from .modules.network import NetworkRequestType  # NOt needed anymore.
# from .modules.network import ServiceStatus
# from .modules.network import StatusID

from .modules.device import Device
from .service.template import ServiceClass
from .service.iot_api import IoTAPI

from .modules.value import Value
# from .modules.value import Delta  # Note: Not ready yet!
# from .modules.value import Period  # Note: Not ready yet!
from .modules.template import ValueTemplate

from .schema.base_schema import LogValue
from .schema.base_schema import PermissionType

from .service import template as service

from .connections import protocol as connection

from .utils.offline_storage import OfflineStorage
from .utils.certificateread import certificate_info_extraction
from .utils.offline_storage import OfflineStorageFiles

from .utils import observer
from .utils import name_check

# #############################################################################
#                             __init__ Setup Stuff
# #############################################################################

__version__ = "v0.7.0"
__auther__ = "Seluxit A/S"

__all__ = [
    'Network',
    'Device',
    'Value',
    'onStatusChange',
    'config',
    'createNetwork',
    'connect',
    'disconnect',
    'close',
    'OfflineStorage',
    'service',
    'connection',
    'ValueTemplate',
    'PermissionType',
    'LogValue',
]


# #############################################################################
#                  Import Stuff for setting up WappstoIoT
# #############################################################################

__log = logging.getLogger("wappstoiot")
__log.addHandler(logging.NullHandler())

# #############################################################################
#                             Status Stuff
# #############################################################################


def onStatusChange(
    StatusID: Union[service.StatusID, connection.StatusID],
    callback: Callable[[Union[service.StatusID, connection.StatusID], Any], None]
) -> None:
    """
    Configure an action when the Status have changed.

    def callback(StatusID: StatusID, newStatus: Any):
    """
    observer.subscribe(
        event_name=StatusID,
        callback=callback
    )


# #############################################################################
#                             Config Stuff
# #############################################################################

__config_folder: Path
__the_connection: Optional[ServiceClass] = None
__connection_closed: bool = False
__ping_pong_thread_killed = threading.Event()
__offline_storage_thread_killed = threading.Event()


class ConnectionTypes(str, Enum):
    IOTAPI = "jsonrpc"
    RESTAPI = "HTTPS"


def config(
    config_folder: Union[Path, str] = ".",  # Relative to the main.py-file.
    connection: ConnectionTypes = ConnectionTypes.IOTAPI,
    # JPC_timeout=3
    # mix_max_enforce="warning",  # "ignore", "enforce"
    # step_enforce="warning",  # "ignore", "enforce"
    fast_send: bool = True,  # TODO: jsonrpc.params.meta.fast=true
    # delta_handling="",
    # period_handling="",
    ping_pong_period_sec: Optional[int] = None,  # Period between a RPC ping-pong.
    # # Send: {"jsonrpc":"2.0","method":"HEAD","id":"PING-15","params":{"url":"/services/2.0/network"}}
    # # receive:
    # {"jsonrpc":"2.0","id":"PING-15","result":{"value":true,"meta":{"server_send_time":"2021-12-15T14:33:11.952629Z"}}}
    offline_storage: Union[OfflineStorage, bool] = False,
    # none_blocking=True,  # Whether the post should wait for reply or not.
) -> None:
    """
    Configure the WappstoIoT settings.

    This function call is optional.
    If it is not called, the default settings will be used for WappstoIoT.
    This function will also connect to the WappstoIoT API on call.
    In the cases that this function is not called, the connection will be
    make when an action is make that requests the connection.

    The 'minMaxEnforce' is default set to "Warning" where a warning is
    reading to log, when the value range is outside the minimum & maximum
    range.
    The 'ignore' is where it do nothing when it is outside range.
    The 'enforce' is where the range are enforced to fit the minimum &
    maximum range. Meaning if it is above the maximum it is changed to
    the maximum, if it is below the minimum, it is set to the minimum value.
    """
    global __config_folder
    global __connection_closed
    global __the_connection
    __the_connection = None
    __connection_closed = False

    if not isinstance(config_folder, Path):
        if config_folder == "." and hasattr(__main__, '__file__'):
            __config_folder = Path(__main__.__file__).absolute().parent / Path(config_folder)
        else:
            __config_folder = Path(config_folder)
    else:
        __config_folder = config_folder

    _setup_ping_pong(ping_pong_period_sec)
    _setup_offline_storage(offline_storage)

    if connection == ConnectionTypes.IOTAPI:
        _setup_IoTAPI(__config_folder, fast_send=fast_send)

    # elif connection == ConnectionTypes.RESTAPI:
    #     # TODO: Find & load configs.
    #     configs: Dict[Any, Any] = {}
    #     _setup_RestAPI(__config_folder, configs)  # FIXME:


def _setup_IoTAPI(
    __config_folder: Path,
    configs: None = None,
    fast_send: bool = False,
) -> None:
    # TODO: Setup the Connection.
    global __the_connection
    kwargs = _certificate_check(__config_folder)
    __the_connection = IoTAPI(
        ca=kwargs['ca'],
        crt=kwargs['crt'],
        key=kwargs['key'],
        fast_send=fast_send,
    )


# def _setup_RestAPI(__config_folder, configs):
#     # TODO: Setup the Connection.
#     global __the_connection
#     token = configs.get("token")
#     login = netrc.netrc().authenticators(configs.end_point)
#     if token:
#         kwargs = {"token": token}
#     elif login:
#         kwargs = {"username": login[0], "password": login[1]}
#     else:
#         raise ValueError("No login was found.")
#     __the_connection = RestAPI(**kwargs, url=configs.end_point)


def _certificate_check(path: Path) -> Dict[str, Path]:
    """Check if the right certificates are at the given path."""
    certi_path = {
        "ca": "ca.crt",
        "crt": "client.crt",
        "key": "client.key",
    }
    r_paths: Dict[str, Path] = {}
    for k, f in certi_path.items():
        r_paths[k] = path / f
        if not r_paths[k].exists():
            raise FileNotFoundError(f"'{f}' was not found in at: {path}")

    return r_paths


def _setup_ping_pong(period_s: Optional[int] = None) -> None:
    # TODO: Test me!
    __ping_pong_thread_killed.clear()
    thread: threading.Timer

    if not period_s:
        return

    # TODO: Need a close check so it do not hold wappsto iot open.
    def _ping() -> None:
        __log.debug("Ping-Pong called!")
        nonlocal thread
        global __ping_pong_thread_killed
        if __ping_pong_thread_killed.is_set():
            return
        if __the_connection is None:
            return
        try:
            thread = threading.Timer(period_s, _ping)
            thread.start()
            __the_connection.ping()
        except Exception:
            __log.exception("Ping-Pong:")
    thread = threading.Timer(period_s, _ping)
    thread.daemon = True
    thread.start()
    atexit.register(lambda: thread.cancel())
    # atexit.register(lambda: __ping_pong_thread_killed.set())


def _setup_offline_storage(
    offlineStorage: Union[OfflineStorage, bool],
) -> None:
    global __the_connection
    global __offline_storage_thread_killed
    __ping_pong_thread_killed.clear()

    if offlineStorage is False:
        return
    # if offlineStorage is True:
    offline_storage: OfflineStorage = OfflineStorageFiles(
        location=__config_folder
    ) if offlineStorage is True else offlineStorage
    # else:
    #     offline_storage: OfflineStorage = offlineStorage

    observer.subscribe(
        service.StatusID.SENDERROR,
        lambda _, data: offline_storage.save(data.model_dump_json(exclude_none=True)) if data else None
    )

    def _resend_logic(status: str, status_data: Any) -> None:
        nonlocal offline_storage
        global __offline_storage_thread_killed
        __log.debug(f"Resend called with: status={status}")
        try:
            __log.debug("Resending Offline data")
            while not __offline_storage_thread_killed.is_set():
                data = offline_storage.load(10)
                if not data:
                    return

                s_data = [json.loads(d) for d in data]
                __log.debug(f"Sending Data: {s_data}")
                if __the_connection is None:
                    return
                __the_connection._resend_data(
                    json.dumps(s_data)
                )

        except Exception:
            __log.exception("Resend Logic")

    observer.subscribe(
        connection.StatusID.CONNECTED,
        _resend_logic
    )


# #############################################################################
#                             Create Stuff
# #############################################################################

def createNetwork(
    name: str,
    description: str = "",
) -> Network:
    """
    Create a new Wappsto Network.

    A Wappsto Network is references to the main grouping, of which multiple
    device are connected.
    """
    global __config_folder
    global __the_connection

    illegal_chars: str = name_check.illegal_characters(name)

    if illegal_chars:
        raise ValueError(
            f"Given name contain a illegal character: {illegal_chars}\n"
            f"May only contain: {name_check.wappsto_letters}"
        )

    if __the_connection is None:
        config()

    if not __config_folder:
        __config_folder = Path('.')

    cer = certificate_info_extraction(crt_path=__config_folder / "client.crt")
    network_uuid = uuid.UUID(cer.get('subject', {}).get('commonName'))

    atexit.register(close)

    return Network(
        name=name,
        connection=cast(ServiceClass, __the_connection),
        network_uuid=network_uuid,
        description=description
    )

# -------------------------------------------------------------------------
#   Connection methods
# -------------------------------------------------------------------------


def connect() -> None:
    """NOT Implemented yet."""
    pass


def disconnect() -> None:
    """NOT Implemented yet."""
    pass


def close() -> None:
    """Close down the connection to wappsto."""
    atexit.unregister(close)
    __ping_pong_thread_killed.set()
    __offline_storage_thread_killed.set()
    # atexit._run_exitfuncs()
    global __connection_closed
    global __the_connection

    if not __connection_closed and __the_connection is not None:
        __log.info("Closing Wappsto IoT")
        __the_connection.close()
        __the_connection = None
        __connection_closed = True
    # Disconnect
    pass
