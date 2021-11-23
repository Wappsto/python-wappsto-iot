import logging
import random
import string

from contextlib import contextmanager
from enum import Enum

from typing import List
from typing import Optional


import requests

from . import Timestamp


force_trace: bool = False


class TraceStatus(str, Enum):
    PENDING = "pending"  # On Receive
    OK = "ok"            # If Send Successful
    FAIL = "fail"        # If Send Failed.


class TraceWrapper:
    """."""

    def __init__(
        self,
        class_obj: object,
        tracer: object,
        tracing_obj: List[str]
    ):
        self.log = logging.getLogger(__name__)
        self.log.addHandler(logging.NullHandler())
        self.class_obj = class_obj
        self.tracer = tracer
        self.tracing_obj = tracing_obj

    def __getattr__(self, attr_name):
        if attr_name not in self.tracing_obj:
            return getattr(self.class_obj, attr_name)

        def wrapper(*args, **kwargs):
            with self.tracer.tracing():
                getattr(self.class_obj, attr_name)(*args, **kwargs)

        return wrapper


class Trace:
    def __init__(
        self,
        name: str,
        id: Optional[str] = None,
        parent: Optional[str] = None
    ):

        self.log = logging.getLogger(__name__)
        self.log.addHandler(logging.NullHandler())

        self.id = id if id else Trace._generateId()
        self.parent = parent
        self.name = name
        self.__status: TraceStatus = TraceStatus.PENDING
        self.timestamp = Timestamp.timestamp()

    @property
    def status(self) -> str:
        """Returns the Status of the Trace."""
        return self.__status

    @staticmethod
    def _generateId() -> str:
        """Generate a Trace ID."""
        return "WappstoIoT_" + "".join(random.choices(
            string.ascii_letters + string.digits,
            k=10
        ))

    @staticmethod
    def _find_parent_id(jsonrpc_elemt) -> Optional[str]:
        """
        Check if a trace package should be send if so it returns the parent ID.
        """
        if isinstance(jsonrpc_elemt, dict):
            return jsonrpc_elemt.get(
                'params', {}).get(
                'meta', {}).get(
                'trace', None
            )
        return jsonrpc_elemt.params.meta.trace

    @staticmethod
    def trace_check(jsonrpc_elemt: dict, name: str) -> Optional['Trace']:
        global force_trace
        parent = Trace._find_parent_id(jsonrpc_elemt)
        if parent or force_trace:
            t = Trace(
                parent=parent,
                name=name
            )
            t.send_pending(name=name)
            return t
        return None

    @staticmethod
    def trace_list_check(
        jsonrpc_elemts: list,
        name: str
    ) -> Optional[List['Trace']]:
        r_list = []
        for t in jsonrpc_elemts:
            t = Trace.trace_check(t, name=name)
            if t:
                r_list.append(t)
        return r_list

    @contextmanager
    def tracing(self, name: Optional[str] = None):
        """Used when replying on a trace."""
        # self.send_pending(name=name)  # Are send on class creation.
        try:
            yield
        except Exception:
            self.send_failed(name=name)
            raise
        else:
            self.send_ok(name=name)

    def __enter__(self):
        """Used when starting a new trace."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.send_failed()
        else:
            self.send_ok()

    def __repr__(self) -> str:
        return (
            "Trace("
            f"ID={self.id}; "
            f"Parent={self.parent}; "
            f"Status={self.__status})"
        )

    def get_child(self) -> 'Trace':
        return Trace(
            parent=self.id,
            name=f"{self.name} child",
        )

    def send_pending(self, name: Optional[str] = None):
        self._send(name=name, status=TraceStatus.PENDING)

    def send_ok(self, name: Optional[str] = None):
        self._send(name=name, status=TraceStatus.OK)

    def send_failed(self, name: Optional[str] = None):
        self._send(name=name, status=TraceStatus.FAIL)

    def _send(
        self,
        status: TraceStatus,
        name: Optional[str] = None,
    ) -> Optional[dict]:
        """
        Send a Package Trace to Seluxit.

        Package tracing are used to debug, where the given package are lost,
        and/or the timing of the given package through the system.

        A trace package should be send when a JSONRPC object, with a trace value
        in the params, meta field, are received. The trace package should contain
        a status that are set to 'pending'.
        When the reply for the traced Wappsto json are ready to be send
        (to the socket). The Wappsto json's meta field should have the trace filed
        added, with the trace_id & name the pending trace package was send with,
        followed with the sending of another trace-package, where the status 'ok'.
        If for some reason it was not possible to generate a reply (but there
        should have been), the trace package should then be send with the
        'fail' status, on the realization this is the case. 

        Args:
            trace_id: A generated ID, that should be added to
                      the Wappsto json meta trace filed.
            parent_id: The trace-value from the Wappsto json meta field.
            name: A descriptive name.
            status: Status for the traced package.
            timestamp: the timestamp in the ISO format.
                       If not sat, it will be sat in the time of sending.

        Returns:
            True, of the Trace package was send successful,
            False, if it was not.
        """
        self.__status = status
        params = {
            "id": self.id,
            "name": name if name else self.name,
            "status": status,
            "timestamp": self.timestamp
        }
        if self.parent:
            params["parent"] = self.parent

        self.log.info(f"Trace id: {self.id}")

        r_data = requests.post(
            url='https://tracer.iot.seluxit.com/trace',
            params=params
        )
        self.log.debug(f"Trace reply: {r_data.text}")

        if r_data.status_code >= 300:
            self.log.error(f"Trace http error code: {r_data.status_code}")
            return None

        self.log.debug("Trace send!")

        return params
