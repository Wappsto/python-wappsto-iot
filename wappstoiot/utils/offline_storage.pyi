import abc
from _typeshed import Incomplete
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterator, List, Optional, Union

class OfflineStorage(ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def save(self, data: str) -> None: ...
    @abstractmethod
    def load(self, max_count: Optional[int] = ...) -> List[str]: ...

class OfflineStorageFiles(OfflineStorage):
    log: Incomplete
    loc: Incomplete
    suffix: str
    def __init__(self, location: Union[Path, str]) -> None: ...
    def auto_save(self, data: str) -> Iterator[None]: ...
    def save(self, data: str) -> None: ...
    def load(self, max_count: Optional[int] = ...) -> List[str]: ...
