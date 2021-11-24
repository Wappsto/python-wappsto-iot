"""
"""
import logging
import time

from abc import ABC
from abc import abstractmethod
from contextlib import contextmanager
from pathlib import Path


from typing import List
from typing import Optional
from typing import Union


class OfflineStorage(ABC):
    @abstractmethod
    def save(self, data: str): ...
    @abstractmethod
    def load(self, max_count: Optional[int] = None) -> List[str]: ...


class OfflineStorageFiles(OfflineStorage):
    """
    Timed over 1M runs.

    In [5]: kk = write()               
    Time used per run: 40_965.816834ns 
                                       
    In [7]: kk = read()                
    Time used per run: 173_536.595006ns
    """
    def __init__(self, location: Union[Path, str]):
        self.log = logging.getLogger(__name__)
        self.log.addHandler(logging.NullHandler())

        if not isinstance(location, Path):
            location = Path(location)

        if location.is_file():
            raise NotADirectoryError(
                f"The given location need to be a directory, not: {location}"
            )
        self.loc = location

        self.suffix = ".data"
        self.loc.mkdir(exist_ok=True)
        self.log.info(f"Location created: {self.loc}")
        self._files = sorted(
            x for x in self.loc.iterdir()
            if x.is_file() and x.suffixes[-1] == self.suffix
        )

    def _sort_files(self, count) -> List[Path]:
        temp = self._files[:count]
        del self._files[:count]
        return temp     

    @contextmanager
    def auto_save(self, data: str):
        """Used when replying on a trace."""
        # self.send_pending(name=name)  # Are send on class creation.
        try:
            yield
        except Exception:
            self.save(data=data)
            raise

    def save(self, data: str):
        self.log.debug(f"Saving data: {data}")
        datafile = self.loc / (str(time.perf_counter_ns()) + self.suffix)
        self.log.debug(f"Save to file: {datafile}")
        with datafile.open(mode="w") as file:
            file.write(f"{data}")
        self._files.append(datafile)

    def load(self, max_count: Optional[int] = None) -> List[str]:
        self.log.debug(f"Load {max_count} lines.")
        data_files = self._sort_files(max_count)
        data = []
        for data_file in data_files:
            with data_file.open(mode="r") as file:
                data.append(file.read())
            self.log.debug(f"File Loaded: {data_file}")
            data_file.unlink()
        return data
