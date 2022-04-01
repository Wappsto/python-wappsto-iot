"""This the the Simple Wappsto Python user-interface to the Wappsto devices."""

# #############################################################################
#                             MOdules Import Stuff
# #############################################################################


import __main__
import atexit
import logging

from pathlib import Path
from enum import Enum


from typing import Any, Dict, Optional, Union, Callable, List, Tuple


from .modules.network import Network

from .modules.device import Device
from .service.template import ServiceClass
from .service.iot_api import IoTAPI

from .modules.value import Value
# from .modules.value import Delta  # Note: Not ready yet!
# from .modules.value import Period  # Note: Not ready yet!
from .modules.value import PermissionType
from .modules.template import ValueTemplate

from .service import template as service

from .connections import protocol as connection

from .utils.certificateread import CertificateRead

from .plugins.plugin_template import PlugInTemplate
from .plugins.ping_pong import PingPong
from .plugins.offline_storage import OfflineStorageFiles

from .utils import observer
from .utils import name_check

# #############################################################################
#                             __init__ Setup Stuff
# #############################################################################

__version__ = "v0.6.2"
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
    'service',
    'connection',
    'ValueTemplate',
    'PermissionType'
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
):
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


class ConnectionTypes(str, Enum):
    IOTAPI = "jsonrpc"
    RESTAPI = "HTTPS"


def config(
    config_folder: Union[Path, str] = ".",  # Relative to the main.py-file.
    # connection: ConnectionTypes = ConnectionTypes.IOTAPI,
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
    offline_storage: bool = False,
    # none_blocking=True,  # Whether the post should wait for reply or not.
    plugins: List[Tuple[PlugInTemplate, Dict[str, Any]]] = None
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

    if plugins is None:
        plugins = []

    if not isinstance(config_folder, Path):
        if config_folder == "." and hasattr(__main__, '__file__'):
            __config_folder = Path(__main__.__file__).absolute().parent / Path(config_folder)
        else:
            __config_folder = Path(config_folder)
    else:
        __config_folder = config_folder

    if offline_storage is True:
        plugins.append((OfflineStorageFiles, {}))

    if ping_pong_period_sec is not None:
        plugins.append((PingPong, {"period_s": ping_pong_period_sec}))

    IoTkwargs = _certificate_check(__config_folder)
    __the_connection = IoTAPI(
        ca=IoTkwargs['ca'],
        crt=IoTkwargs['crt'],
        key=IoTkwargs['key'],
        fast_send=fast_send
    )

    setup_plugins(plugins=plugins)
    # TODO: POST Status change. (Connected)


def _certificate_check(path) -> Dict[str, Path]:
    """
    Check if the right certificates are at the given path.
    """
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


# #############################################################################
#                             Plugin Stuff
# #############################################################################

_plugins_list: List[PlugInTemplate] = []


def setup_plugins(
    plugins: List[Tuple[PlugInTemplate, Dict[str, Any]]]
):
    for x in plugins:
        setup_plugin(x[0], x[1])


def close_plugins():
    global _plugins_list
    for plugin in _plugins_list:
        plugin.close()


def setup_plugin(plugin: PlugInTemplate, params: Dict[str, Any]):
    global __the_connection
    global __config_folder
    global observer

    pg: PlugInTemplate = plugin(
        config_location=__config_folder,
        service=__the_connection,
        observer=observer,
        **params
    )

    _plugins_list.append(pg)


# #############################################################################
#                             Create Stuff
# #############################################################################

def createNetwork(
    name: str,
    description: str = "",
) -> Network:
    global __config_folder
    global __the_connection

    if not name_check.legal_name(name):
        raise ValueError(
            "Given name contain a ilegal character."
            f"May only contain: {name_check.wappsto_letters}"
        )

    if not __the_connection:
        config()

    if not __config_folder:
        __config_folder = Path('.')

    cer = CertificateRead(crt=__config_folder / "client.crt")
    uuid = cer.network

    atexit.register(close)

    return Network(
        name=name,
        connection=__the_connection,
        network_uuid=uuid,
        description=description
    )

# -------------------------------------------------------------------------
#   Connection methods
# -------------------------------------------------------------------------


def connect():
    # TODO: Connect with same settings as before the disconnect.
    # TODO: POST Status change. (Connecting)
    pass
    # TODO: POST Status change. (Connected)


def disconnect():
    global __connection_closed
    global __the_connection
    # TODO: POST Status change. (Disconnecting)
    if not __connection_closed and __the_connection is not None:
        __log.info("Disconnecting Wappsto IoT")
        __the_connection.close()
        __connection_closed = True


def close():
    """."""
    # TODO: POST Status change. (Closing)
    atexit.unregister(close)
    close_plugins()
    observer.unsubscribe_all()
    # atexit._run_exitfuncs()
    disconnect()
    __log.info("Wappsto IoT Closed")
