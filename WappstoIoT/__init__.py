"""This the the Simple Wappsto Python userinterface to the Wappsto devices."""
from enum import Enum
from pathlib import Path

from typing import Any
from typing import Callable
from typing import Optional
from typing import Type
from typing import Union


class PermissionType(str, Enum):
    """All possible Value Permission Types."""

    read = "r"
    write = "w"
    readwrite = "rw"


class ValueType(str, Enum):
    """Each ValueType have a range."""

    default = "Default"
    temperature = "Temperature"
    speed = "Speed"
    ...


class Status(Enum, str):
    STARTING = "Starting"
    CONNECTING = "Connecting"
    CONNECTED = "Connected"
    INITIALIZING = "Initializing"
    STARTING_THREADS = "Starting Threads"
    RUNNING = "Running"
    RECONNECTING = "Reconnecting"
    DISCONNECTING = "Disconnecting"


class Event(Enum, str):
    pass


class Value:

    @property
    def data(self):
        """.
        Callback:
            Value: the Object that have had a request for.
            str: Name of what to do something with.
        """
        pass

    def onChange(
        self,
        callback: Callable[[Value, str], None],
    ) -> None:
        """
        For whne something have changed.
        Should never happen her!
        """
        pass

    def onReport(
        self,
        callback: Callable[[Value, str], None],
    ) -> None:
        """Triggered on Data change, even if the data was changed to the same value."""
        pass

    def onRequest(
        self,
        callback: Callable[[Value, Enum, str, Any], None],
    ) -> None:
        """
        For Refresh & Control. When We are asked to be something

        Callback:
            Value: the Object that have had a request for.
            Enum: Which type of Request have happened.
            str: Name of what to do something with.
            any: The Data.
        """
        pass

    def onControl(
        self,
        callback: Callable[[Value, Any], None],
    ) -> None:
        pass

    def onRefresh(
        self,
        callback: Callable[[Value], None],
    ) -> None:
        """For Refresh & Control. When We are asked to be something"""
        pass

    # def onDelete(
    #     self,
    #     callback: Callable[[Value], None],
    # ) -> None:
    #     """For Refresh & Control. When We are asked to be something"""
    #     pass

    async def update(self, Type: str) -> None:
        """Update a parameter in the Value structure."""
        pass

    async def report(self, value: Any) -> None:
        """Calls Update report."""
        pass

    async def control(self, value: Any) -> None:
        pass


class Device:
    def onChange(
        self,
        callback: Callable[[str, Any], None],
        change_type=None
    ) -> None:
        pass

    def onRequest(
        self,
        callback: Callable[[str, Any], None],
        change_type=None
    ) -> None:
        pass

    async def update(self, Type: str) -> None:
        """Update a parameter in the Value structure."""
        pass

    async def createValue(
        self,
        name: str,
        value_id: Optional[int] = None,
        value_type: Optional[ValueType] = ValueType.default,
        permission: Optional[PermissionType] = PermissionType.readwrite,
        min: Optional[Union[int, float]] = None,
        max: Optional[Union[int, float]] = None,
        step: Optional[Union[int, float]] = None,
        encoding: Optional[str] = None,
        enforce_range: Optional[bool] = False,
        period: Optional[int] = None,  # in Sec
        delta: Optional[Union[int, float]] = None,
        type: Optional[str] = None,
        description: Optional[str] = None,
        meaningful_zero: Optional[str] = None,
        si_conversion: Optional[str] = None,
        unit: Optional[str] = None,
    ) -> Type[Value]:
        """."""
        pass

    def onDelete(
        self,
        callback: Callable[[Value], None],
    ) -> None:
        """For Refresh & Control. When We are asked to be something"""
        pass


def config(
    configFolder: Path,
    name: Optional[str] = "TheNetwork",
    description: Optional[str] = "",
    mixMaxEnforce="warning",  # "ignore", "enforce"
    pingPongPeriod=0,
) -> None:
    """."""
    # Connect
    pass


def onChange(
    callback: Callable[[str, Event], None],
    change_type="Status"
) -> None:
    """."""
    pass

    def Networkcallback(name: str, event: Event, /) -> None:
        """."""
        pass


async def createDevice(
    name: Optional[str] = "DefaultDevice",
    device_id: Optional[int] = None, 
    manufacturer: Optional[str] = None,
    product: Optional[str] = None,
    version: Optional[str] = None,
    serial: Optional[str] = None,
    description: Optional[str] = None,
) -> Device:
    """."""
    pass


def close(save: Optional[bool] = False):
    """."""
    # Disconnect
    pass


def getStatus() -> Status:
    """."""
    pass
