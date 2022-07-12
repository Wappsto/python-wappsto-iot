"""
"""
import logging
import time
import json
import threading

from contextlib import contextmanager
from pathlib import Path

from typing import Any
from typing import List
from typing import Optional
from typing import Union

from pydantic import BaseModel

from .plugin_template import PlugInTemplate
from .plugin_template import ConnectionTemplate
# from .plugin_template import ModuleTemplate
from .plugin_template import ServiceTemplate
from ..utils import observer


class OfflineStorageFiles(PlugInTemplate):
    """
    Timed over 1M runs.

    In [5]: kk = write()
    Time used per run: 40_965.816834ns

    In [7]: kk = read()
    Time used per run: 173_536.595006ns
    """
    def __init__(
        self,
        config_location: Union[Path, str],
        service: ServiceTemplate.ServiceClass,
        observer: observer,
        **kwargs
    ):
        self.log = logging.getLogger(__name__)
        self.log.addHandler(logging.NullHandler())

        self.service = service
        self.observer = observer

        self.killed = threading.Event()

        if not isinstance(config_location, Path):
            config_location = Path(config_location)

        if config_location.is_file():
            raise NotADirectoryError(
                f"The given location need to be a directory, not: {config_location}"
            )
        self.loc = config_location

        self.suffix = ".data"
        self.loc.mkdir(exist_ok=True)
        self.log.info(f"Location created: {self.loc}")
        self._files = sorted(
            x for x in self.loc.iterdir()
            if x.is_file() and x.suffixes and x.suffixes[-1] == self.suffix
        )
        self._setup_subscribtions()

    def _setup_subscribtions(self):
        self.observer.subscribe(
            ServiceTemplate.StatusID.SENDERROR,
            self.save
        )
        self.observer.subscribe(
            ConnectionTemplate.StatusID.CONNECTED,
            self._resend_logic
        )

    def _cancel_subscribtions(self):
        self.observer.unsubscribe(
            ServiceTemplate.StatusID.SENDERROR,
            self.save
        )
        self.observer.unsubscribe(
            ConnectionTemplate.StatusID.CONNECTED,
            self._resend_logic
        )

    def _sort_files(self, count) -> List[Path]:
        temp = self._files[:count]
        del self._files[:count]
        return temp

    def _resend_logic(self, status, status_data):
        self.log.debug(f"Resend called with: status={status}")
        try:
            self.log.debug("Resending Offline data")
            while not self.killed.is_set():
                data = self.load(10)
                if not data:
                    return

                s_data = [json.loads(d) for d in data]
                self.log.debug(f"Sending Data: {s_data}")
                self.service._resend_data(
                    json.dumps(s_data)
                )

        except Exception:
            self.log.exception("Resend Logic")

    @contextmanager
    def auto_save(self, pydantic_data: BaseModel):
        """Used when replying on a trace."""
        # self.send_pending(name=name)  # Are send on class creation.
        try:
            yield
        except Exception:
            self.save(event_name="", pydantic_data=pydantic_data)
            raise

    def save(self, event_name: Any, pydantic_data: BaseModel) -> None:
        if not pydantic_data:
            return

        data = pydantic_data.json(exclude_none=True)
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

    def close(self):
        self.killed.set()
        self._cancel_subscribtions()
