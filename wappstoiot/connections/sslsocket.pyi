from ..utils import observer as observer
from .protocol import Connection as Connection, StatusID as StatusID
from _typeshed import Incomplete
from pathlib import Path
from typing import Any, Callable, Optional, Union

class TlsSocket(Connection):
    log: Incomplete
    observer_name: str
    observer: Incomplete
    send_ready: Incomplete
    address: Incomplete
    port: Incomplete
    socket_timeout: int
    RECEIVE_SIZE: int
    killed: Incomplete
    ssl_context: Incomplete
    def __init__(self, address: str, port: int, ca: Path, crt: Path, key: Path) -> None: ...
    def send(self, data: Union[str, bytes]) -> bool: ...
    def receive(self, parser: Callable[[bytes], Any]) -> Any: ...
    def connect(self) -> Optional[bool]: ...
    def reconnect(self, retry_limit: Optional[int] = ...) -> bool: ...
    def disconnect(self) -> None: ...
    socket: Incomplete
    raw_socket: Incomplete
    def close(self) -> None: ...
