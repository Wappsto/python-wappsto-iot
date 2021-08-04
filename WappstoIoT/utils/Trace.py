import logging
import datetime

from enum import Enum
from typing import Optional

import requests

from utils import Timestamp

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class TraceStatus(str, Enum):
    PENDING = "pending"  # On Receive
    OK = "ok"            # If Send Successful
    FAIL = "fail"        # If Send Failed.


def send(
    trace_id: str,
    parent: str,
    name: str,
    status: TraceStatus,
    timestamp: Optional[datetime.datetime] = None
) -> bool:
    """
    Send a Package Trace to Seluxit.

    Package tracing are used to debug, where the given package are lost,
    and/or the timing of the given package through the system.

    A trace package should be send when a Wappsto json, with a trace value
    in the meta field, are received. The trace package should contain
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
        parent: The trace-value from the Wappsto json meta field.
        name: A descriptive name.
        status: Status for the traced package.
        timestamp: the timestamp in the ISO format.
                   If not sat, it will be sat in the time of sending.

    Returns:
        True, of the Trace package was send successful,
        False, if it was not.
    """
    params = {
        "id": trace_id,
        "parent": parent,
        "name": name,
        "status": status,
        "timestamp": timestamp if timestamp else Timestamp.timestamp()
    }

    r_data = requests.post(
        url='https://tracer.iot.seluxit.com/trace',
        params=params
    )
    log.info(f"Trace data: {params}")
    log.debug(f"Trace reply: {r_data.text}")

    if r_data.status_code >= 300:
        log.error(f"Trace http error code: {r_data.status_code}")
        return False

    log.debug("Trace send!")

    return True
