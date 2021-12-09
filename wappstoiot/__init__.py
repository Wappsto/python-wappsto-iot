"""This the the Simple Wappsto Python user-interface to the Wappsto devices."""

# #############################################################################
#                             MOdules Import Stuff
# #############################################################################

from .modules.network import Network
# from .modules.network import ConnectionStatus
# from .modules.network import ConnectionTypes
# from .modules.network import NetworkChangeType  # NOt needed anymore.
# from .modules.network import NetworkRequestType  # NOt needed anymore.
# from .modules.network import ServiceStatus
# from .modules.network import StatusID

from .modules.device import Device
from .service.template import ServiceClass

from .modules.value import Value
from .modules.value import Delta
from .modules.value import Period
from .modules.value import PermissionType
from .modules.value import ValueBaseType
from .modules.template import ValueType


# #############################################################################
#                             __init__ Setup Stuff
# #############################################################################

__version__ = "v0.5.3"
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
    'StatusID',
]


# #############################################################################
#                  Import Stuff for setting up WappstoIoT
# #############################################################################

import __main__
import atexit
import netrc
import json
import logging

from pathlib import Path
from enum import Enum


from typing import Any, Dict, Optional, Union, Callable


from .utils.certificateread import CertificateRead
from .utils.offline_storage import OfflineStorage
from .utils.offline_storage import OfflineStorageFiles

from .service.iot_api import IoTAPI

# from .utils import observer 


__log = logging.getLogger("wappstoiot")
__log.addHandler(logging.NullHandler())

# #############################################################################
#                             Status Stuff
# #############################################################################


from .utils import observer 
from .connections import protocol as connection
from .service import template as service


class StatusID(str, Enum):
    CONNECTION = "CONNECTION"
    SERVICE = "SERVICE"


# TODO: TEST the Status thingy.
ConnectionStatus = connection.Status.DISCONNETCED
ServiceStatus = service.Status.IDLE


def __connectionStatus(
    layer: StatusID,
    newStatus: connection.Status
):
    global ConnectionStatus
    ConnectionStatus = newStatus


def __serviceStatus(
    layer: StatusID,
    newStatus: service.Status
):
    global ServiceStatus
    ServiceStatus = newStatus


def subscribe_all_status():
    observer.subscribe(
        event_name=StatusID.CONNECTION,
        callback=__connectionStatus
    )
    observer.subscribe(
        event_name=StatusID.SERVICE,
        callback=__serviceStatus
    )


def onStatusChange(
    layer: StatusID,
    callback: Callable[[StatusID, str], None]
):
    """
    Configure an action when the Status have changed.

    def callback(layer: LayerEnum, newStatus: str):

    """
    observer.subscribe(
        event_name=layer,
        callback=callback
    )


# #############################################################################
#                             Config Stuff
# #############################################################################

__config_folder: Optional[Path] = None
__the_connection: Optional[ServiceClass] = None


class ConnectionTypes(str, Enum):
    IOTAPI = "jsonrpc"
    RESTAPI = "HTTPS"


def config(
    config_folder: Union[Path, str] = ".",  # Relative to the main.py-file.
    connection: ConnectionTypes = ConnectionTypes.IOTAPI,
    mix_max_enforce="warning",  # "ignore", "enforce"
    step_enforce="warning",  # "ignore", "enforce"
    delta_handling="",
    period_handling="",
    connect_sync: bool = True,  # Start with a Network GET to sync.  # TODO:
    ping_pong_period: Optional[int] = None,  # Period between a RPC ping-pong.
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

    if not isinstance(config_folder, Path):
        if config_folder == "." and hasattr(__main__, '__file__'):
            __config_folder = Path(__main__.__file__).absolute().parent / Path(config_folder)
        else:
            __config_folder = Path(config_folder)

    _setup_offline_storage(offline_storage)

    if connection == ConnectionTypes.IOTAPI:
        _setup_IoTAPI(__config_folder)

    elif connection == ConnectionTypes.RESTAPI:
        # TODO: Find & load configs.
        configs: Dict[Any, Any] = {}
        _setup_RestAPI(__config_folder, configs)  # FIXME:

    subscribe_all_status()


def _setup_IoTAPI(__config_folder, configs=None):
    # TODO: Setup the Connection.
    global __the_connection
    kwargs = _certificate_check(__config_folder)
    __the_connection = IoTAPI(**kwargs)


def _setup_RestAPI(__config_folder, configs):
    # TODO: Setup the Connection.
    global __the_connection
    token = configs.get("token")
    login = netrc.netrc().authenticators(configs.end_point)
    if token:
        kwargs = {"token": token}
    elif login:
        kwargs = {"username": login[0], "password": login[1]}
    else:
        raise ValueError("No login was found.")
    __the_connection = RestAPI(**kwargs, url=configs.end_point)


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


def _setup_offline_storage(
    offlineStorage: Union[OfflineStorage, bool],
) -> None:
    global __the_connection

    if offlineStorage is False:
        return
    if offlineStorage is True:
        offline_storage: OfflineStorage = OfflineStorageFiles(
            location=__config_folder
        )
    else:
        offline_storage: OfflineStorage = offlineStorage

    observer.subscribe(
        service.Status.SENDERROR,
        lambda _, data: offline_storage.save(data.json(exclude_none=True))
    )

    def _resend_logic(status, data):
        nonlocal offline_storage
        __log.debug(f"Resend called with: status={status}")
        try:
            __log.debug("Resending Offline data")
            while True:
                data = offline_storage.load(10)
                if not data:
                    return

                s_data = [json.loads(d) for d in data]
                __log.debug(f"Sending Data: {s_data}")
                __the_connection._resend_data(
                    json.dumps(s_data)
                )

        except Exception:
            __log.exception("Resend Logic")

    observer.subscribe(
        connection.Status.CONNECTED,
        _resend_logic
    )


# #############################################################################
#                             Create Stuff
# #############################################################################

__connection_closed = False


def createNetwork(
    name: str = "TheNetwork",
    description: str = "",
) -> Network:
    global __config_folder
    global __the_connection

    if not __the_connection:
        config()

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
    pass


def disconnect():
    pass


def close():
    """."""
    global __connection_closed
    global __the_connection

    if not __connection_closed:
        __the_connection.close()
        __connection_closed = True
    # Disconnect
    pass
