import abc
from abc import ABC, abstractmethod
from enum import Enum
from threading import Lock
from typing import Any, Callable, Optional, Union

class StatusID(str, Enum):
    CONNECTING: str
    CONNECTED: str
    DISCONNECTING: str
    DISCONNETCED: str

class Connection(ABC, metaclass=abc.ABCMeta):
    send_ready: Lock
    @abstractmethod
    def send(self, data: Union[str, bytes]) -> bool: ...
    @abstractmethod
    def receive(self, parser: Callable[[bytes], Any]) -> Any: ...
    @abstractmethod
    def connect(self) -> Optional[bool]: ...
    @abstractmethod
    def reconnect(self, retry_limit: Optional[int] = ...) -> bool: ...
    @abstractmethod
    def disconnect(self) -> None: ...
    @abstractmethod
    def close(self) -> None: ...
