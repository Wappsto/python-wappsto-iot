import datetime
import logging
import random
import string

from enum import Enum

from typing import Optional
from typing import Union

import requests

from WappstoIoT.utils import Timestamp
from WappstoIoT.schema.base_schema import WappstoObject


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class TraceStatus(str, Enum):
    PENDING = "pending"  # On Receive
    OK = "ok"            # If Send Successful
    FAIL = "fail"        # If Send Failed.


ForcedTrace = False


def generateId() -> str:
    """Generate a Trace ID."""
    return "WappstoIoT_" + "".join(random.choices(
        string.ascii_letters + string.digits,
        k=10
    ))


def parentId(jsonrpc_elemt: Union[WappstoObject, dict]) -> Union[str, None]:
    """
    Check if a trace package should be send, if so it returns the parent ID.
    """
    log.debug(f"jsonrpc_elemt={jsonrpc_elemt}")
    if isinstance(jsonrpc_elemt, dict):
        return jsonrpc_elemt.get('params', {}).get('meta', {}).get('trace', None)
    return jsonrpc_elemt.meta.trace


def send(
    id: str,
    parent: str,
    name: str,
    status: TraceStatus,
    timestamp: Optional[datetime.datetime] = None
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
    params = {
        "id": id,
        "parent": parent,
        "name": name,
        "status": status,
        "timestamp": timestamp if timestamp else Timestamp.timestamp()
    }

    log.info(f"Trace id: {id}")

    r_data = requests.post(
        url='https://tracer.iot.seluxit.com/trace',
        params=params
    )
    log.debug(f"Trace reply: {r_data.text}")

    if r_data.status_code >= 300:
        log.error(f"Trace http error code: {r_data.status_code}")
        return None

    log.debug("Trace send!")

    return params
