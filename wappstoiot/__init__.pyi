from .connections import protocol as connection
from .modules.device import Device as Device
from .modules.network import Network as Network
from .modules.template import ValueTemplate as ValueTemplate
from .modules.value import PermissionType as PermissionType, Value as Value
from .service import template as service
from .utils.offline_storage import OfflineStorage as OfflineStorage
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional, Union

def onStatusChange(StatusID: Union[service.StatusID, connection.StatusID], callback: Callable[[Union[service.StatusID, connection.StatusID], Any], None]): ...

class ConnectionTypes(str, Enum):
    IOTAPI: str
    RESTAPI: str

def config(config_folder: Union[Path, str] = ..., connection: ConnectionTypes = ..., fast_send: bool = ..., ping_pong_period_sec: Optional[int] = ..., offline_storage: Union[OfflineStorage, bool] = ...) -> None: ...
def createNetwork(name: str, description: str = ...) -> Network: ...
def connect() -> None: ...
def disconnect() -> None: ...
def close() -> None: ...
