import logging

from enum import Enum
from typing import Optional

from utils import observer


class Status(str, Enum):
    DISCONNECTED = "Disconnected"
    CONNECTING = "Connecting"
    CONNECTED = "Connected"
    # Initializing: Inprocess of sending the wappsto init protocol.
    INITIALIZING = "Initializing"
    READY = "Ready"
    RECONNECTING = "Reconnecting"
    DISCONNECTING = "Disconnecting"


class StatusTracing:
    
    def __init__(self, Element: Optional[str] = None):
        log = logging.getLogger(__name__)
        log.addHandler(logging.NullHandler())

        self.state: Status = Status.INITIALIZING

    def change(self, state: Status):
        """
        Change the Status.
        """
        if type(state) is not Status:
            raise TypeError(
                f"The given state, need to be of type: '{__name__}.Status'"
            )
        observer.post("Status change", Status)
        self.state = state
