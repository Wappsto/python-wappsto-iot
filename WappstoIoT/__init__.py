"""This the the Simple Wappsto Python user-interface to the Wappsto devices."""
import datetime

from enum import Enum
from pathlib import Path

from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import Union


class PermissionType(str, Enum):
    """All possible Value Permission Types."""

    READ = "r"
    WRITE = "w"
    READWRITE = "rw"


class Period(str, Enum):
    PERIODIC_REFRESH = "periodic"
    DROP_UNTIL = "drop"


class Delat(str, Enum):
    ONLY_UPDATE_IF = ""
    EXTRA_UPDATES = ""


class ValueBaseType(str, Enum):
    """Internal use only!."""
    STRING = "string"
    NUMBER = "number"
    BLOB = "blob"
    XML = "xml"


class ValueType(str, Enum):
    """
    Predefined ValueTypes.

    Each of the predefined ValueTypes, have default
    value parameters set, which include BaseType, name,
    permission, range, step and the unit.
    """

    DEFAULT = "Default"
    STRING = "String"
    NUMBER = "Number"
    BLOB = "Blob"
    XML = "Xml"
    TEMPERATURE = "Temperature"
    SPEED = "Speed"
    BOOLEAN = "Boolean"
    LATITUDE = "Latitude"
    LONGITUDE = "Longitude"
    ...


valueSettings: Dict[ValueType, Dict[str, Union[int, float, str, None]]] = {
    ValueType.DEFAULT: {
        "type": ValueBaseType.NUMBER,
        "name": "number",
        "permission": PermissionType.READWRITE,
        "min": 0,
        "max": 255,
        "step": 1,
        "unit": None
    },
    ValueType.STRING: {
        "type": ValueBaseType.STRING,
        "name": "string",
        "permission": PermissionType.READWRITE,
        "max": 64,
        "encoding": "utf-8",
        "unit": None
    },
    ValueType.NUMBER: {
        "type": ValueBaseType.NUMBER,
        "name": "number",
        "permission": PermissionType.READWRITE,
        "min": -1e+380,  # UNSURE(MBK): !!
        "max": 1e+380,
        "step": 1e-038,
        "unit": None
    },
    ValueType.BLOB: {
        "type": ValueBaseType.BLOB,
        "name": "Blob",
        "permission": PermissionType.READWRITE,
        "max": 64,
        "encoding": "base64",
        "unit": None
    },
    ValueType.XML: {
        "type": ValueBaseType.XML,
        "name": "Xml",
        "permission": PermissionType.READWRITE,
        "max": 64,
        "encoding": "xml",
        "unit": None
    },
    ValueType.LATITUDE: {
        "type": ValueBaseType.NUMBER,
        "name": "latitude",
        "permission": PermissionType.READ,
        "min": -90,
        "max": 90,
        "step": 0.000001,
        "unit": "°N"
    },
    ValueType.LONGITUDE: {
        "type": ValueBaseType.NUMBER,
        "name": "longitude",
        "permission": PermissionType.READ,
        "min": -180,
        "max": 180,
        "step": 0.000001,
        "unit": "°E"
    },
    ValueType.BOOLEAN: {
        "type": ValueBaseType.NUMBER,
        "name": "boolean",
        "permission": PermissionType.READWRITE,
        "mapping": None,  # dict,
        "ordered_mapping": None,  # Boolean
        "meaningful_zero": None,  # Boolean
        "min": 0,
        "max": 1,
        "step": 1,
        "unit": "Boolean"
    },
}


# class Status(str, Enum):
#     STARTING = "Starting"
#     CONNECTING = "Connecting"
#     CONNECTED = "Connected"
#     INITIALIZING = "Initializing"
#     STARTING_THREADS = "Starting Threads"
#     RUNNING = "Running"
#     RECONNECTING = "Reconnecting"
#     DISCONNECTING = "Disconnecting"


SelfValue = TypeVar('SelfValue', bound='Value')


class Value:

    class RequestType(str, Enum):
        refresh = "refresh"
        control = "control"
        delete = "delete"

    class ChangeType(str, Enum):
        report = "report"
        delta = "delta"
        period = "period"
        name = "name"
        description = "description"
        unit = "unit"
        min = "min"
        max = "max"
        step = "step"
        encoding = "encoding"
        meaningful_zero = "meaningful_zero"
        state = "state"  # UNSURE: ?!!?

    @property
    def data(self) -> Union[str, int, float]:
        """
        Returns the last value.

        The returned value will be the last Report value,
        unless there isn't one, then it will be the Control value.
        """
        pass

    @property
    def name(self) -> str:
        """Returns the name of the value."""
        pass

    @property
    def valueID(self) -> str:
        """
        Returns the value ID of the value.

        The value ID is needed to make sure that it is the same value after
        a name change, and or after a reboot, if something have changed.
        """
        pass

    def onChange(
        self,
        callback: Callable[[SelfValue, ChangeType], None],
    ) -> None:
        """
        Add a trigger on when change have been make.

        A change on the Value typically will mean that a parameter, like
        period or delta or report value have been changed,
        from the server/user side.

        Callback:
            ValueObj: The Object that have had a change to it.
            ChangeType: Name of what have change in the object.
        """
        pass

    def onReport(
        self,
        callback: Callable[[SelfValue, Union[str, int, float]], None],
    ) -> None:
        """
        Add a trigger on when Report data change have been make.

        This trigger even if the Report data was changed to the same value.

        Callback:
            Value: the Object that have had a Report for.
            Union[str, int, float]: The Value of the Report change.
        """
        pass

    def onRequest(
        self,
        callback: Callable[[SelfValue, RequestType, str, Any], None],
    ) -> None:
        """
        For Refresh & Control. When We are asked to be something

        # UNSURE(MBK): Name & Event, is the Same! o.0

        Callback:
            ValueObj: the Object that have had a request for.
            Event: Which type of Request have happened.
            str: Name of what to do something with.
            any: The Data.
        """
        pass

    def onControl(
        self,
        callback: Callable[[SelfValue, Union[str, int, float]], None],
    ) -> None:
        """
        Add trigger for when a Control request have been make.

        A Control value is typical use to request a new target value,
        for the given value.

        Callback:
            ValueObj: This object that have had a request for.
            any: The Data.
        """
        pass

    def onRefresh(
        self,
        callback: Callable[[SelfValue], None],
    ) -> None:
        """
        Add trigger for when a Refresh where requested.

        A Refresh is typical use to request a update of the report value,
        in case of the natural update cycle is not fast enough for the user,
        or a extra sample are wanted at that given time.

        Callback:
            ValueObj: This object that have had a refresh request for.
        """
        pass

    # def onDelete(
    #     self,
    #     callback: Callable[[SelfValue], None],
    # ) -> None:
    #     """For Refresh & Control. When We are asked to be something"""
    #     pass

    def change(self, name: str, value: Any) -> None:
        """
        Update a parameter in the Value structure.

        A parameter that a device can have that can be updated could be:
         - Name
         - Description
         - Unit
         - min/max/step/encoding
         - period
         - delta
         - meaningful_zero
        """
        pass

    def delete(self):
        pass

    def report(
        self,
        value: Union[int, float, str, None],
        timestamp: Optional[datetime.datetime] = None
    ) -> None:
        """
        Report the new current value to Wappsto.

        The Report value is typical a measured value from a sensor,
        whether it is a GPIO pin, a analog temperature sensor or a
        device over a I2C bus.
        """
        pass

    def control(
        self,
        value: Union[int, float, str, None],
        timestamp: Optional[datetime.datetime] = None
    ) -> None:
        """
        Report the a new control value to Wappsto.

        A Control value is typical only changed if a target wanted value,
        have changed, whether it is because of an on device user controller,
        or the target was outside a given range.
        """
        pass


class Device:

    class RequestType(str, Enum):
        refresh = "refresh"
        delete = "delete"

    class ChangeType(str, Enum):
        value = "value"
        name = "name"
        manufacturer = "manufacturer"
        product = "product"
        version = "version"
        serial = "serial"
        description = "description"

    def onRefresh(  # TODO: Change me!
        self,
        callback: Callable[[SelfValue], None],
    ) -> None:
        """
        Add trigger for when a Refresh where requested.

        A Refresh is typical use to request a update of the report value,
        in case of the natural update cycle is not fast enough for the user,
        or a extra sample are wanted at that given time.

        Callback:
            ValueObj: This object that have had a refresh request for.
        """
        pass

    def onChange(
        self,
        callback: Callable[[str, Any], None],
        change_type: Optional[Union[List[ChangeType], ChangeType]] = None
    ) -> None:
        """
        Configure a callback for when a change to the Device have occurred.
        """
        pass

    def onRequest(
        self,
        callback: Callable[[str, Any], None],
        request_type: Optional[RequestType] = None
    ) -> None:
        """
        Configure a callback for when a request have been make for the Device.
        """
        pass

    def change(self, change_type: ChangeType) -> None:
        """
        Update a parameter in the Device structure.

        A parameter that a device can have that can be updated could be:
         - manufacturer
         - product
         - version
         - serial
         - description
        """
        pass

    def delete(self):
        pass

    def createValue(
        self,
        name: Optional[str] = None,
        value_id: Optional[int] = None,
        value_type: Optional[ValueType] = ValueType.DEFAULT,
        permission: Optional[PermissionType] = PermissionType.READWRITE,
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
    ) -> Value:
        """
        Create a Wappsto Value.

        A Wappsto Value is where the changing data can be found & are handled.

        If a value_type have been set, that means that the parameters like:
        name, permission, min, max, step, encoding & unit have been set
        for you, to be the right settings for the given type. But you can
        still change it, if you choose sow.
        """
        pass

    def onDelete(
        self,
        callback: Callable[[Value], None],
    ) -> None:
        """
        Configure an action when a Delete on this Device have been Requested.

        Normally when a Delete have been requested,
        it is when it is not wanted anymore.
        Which mean that all the device and it's values have to be removed,
        and the process of setting up the device, should be executed again.
        This could result in the same device are created again, or if the
        device was not found, it will just be removed.
        """
        pass


class NetworkChangeType(str, Enum):
    description = "description"
    device = "device"
    info = "info"
    name = "name"


class NetworkRequestType(str, Enum):
    refresh = "refresh"
    delete = "delete"


# class status:
#     Connection -> *REf
#


def config(
    configFolder: Union[Path, str] = "config/",  # Relative to the main.py-file.
    name: Optional[str] = "TheNetwork",
    description: Optional[str] = "",
    mixMaxEnforce="warning",  # "ignore", "enforce"
    stepEnforce="warning",  # "ignore", "enforce"
    connectSync: bool = False,  # Start with a Network GET to sync.
    pingPongPeriod: Optional[int] = None,
    storeQueue: Optional[bool] = False,
) -> None:
    """
    Configure the WappstoIoT settings.

    This function call is optional.
    If it is not called, the default settings will be used for WappstoIoT.
    This function will also connect to the WappstoIoT API on call.
    In the cases that this function is not called, the connection will be
    make when an action is make that requests the connection.

    The 'minMaxEnforce' is default set to "Warning" where a warning is
    reading to log, when the value range is outside the minimum & maximum
    range.
    The 'ignore' is where it do nothing when it is outside range.
    The 'enforce' is where the range are enforced to fit the minimum &
    maximum range. Meaning if it is above the maximum it is changed to
    the maximum, if it is below the minimum, it is set to the minimum value.
    """
    pass


def clean() -> None:
    """
    Remove local storage, and references to the Wappsto data-model.
    """
    pass


def onChange(
    callback: Callable[[str, NetworkChangeType], None],
) -> None:
    """
    Configure a callback for when a change to the Network have occurred.

    # UNSURE(MBK): Name & Event, is the Same! o.0

    # def Networkcallback(name: str, event: NetworkChangeType, /) -> None:
    #     pass
    """
    # POST/PUT
    pass


def onRequest(
    callback: Callable[[str, NetworkRequestType], None],
) -> None:
    """
    Configure a callback for when a request of the Network have been requested.

    # UNSURE(MBK): Name & Event, is the Same! o.0

    # def Networkcallback(name: str, event: NetworkRequestType, /) -> None:
    #     pass
    """
    # GET/DELETE
    pass


def onRefresh(
    callback: Callable[[None], None]
):
    """
    Configure an action when a refresh Network have been Requested.

    Normally when a refresh have been requested on a Network, ...
    ...
    """
    pass


def onDelete(
    callback: Callable[[None], None]
):
    """
    Configure an action when a Delete Network have been Requested.

    Normally when a Delete have been requested on a Network,
    it is when it is not wanted anymore, and the Network have been
    unclaimed. Which mean that all the devices & value have to be
    recreated, and/or the program have to close.
    """
    pass


def createDevice(
    name: Optional[str] = None,
    device_id: Optional[int] = None, 
    manufacturer: Optional[str] = None,
    product: Optional[str] = None,
    version: Optional[str] = None,
    serial: Optional[str] = None,
    description: Optional[str] = None,
) -> Device:
    """
    Create a new Wappsto Device.

    A Wappsto Device is references something that is attached to the network
    that can be controlled or have values that can be reported to Wappsto.

    This could be a button that is connected to this unit,
    or in the case of this unit is a gateway, it could be a remote unit.
    """
    # if not device_id:
    #     device_id = max(x.id for x in __device_list) + 1
    # if not name:
    #     name = str(device_id)
    pass


def change():
    pass


def delete():
    pass


class LayerEnum(str, Enum):
    # TODO: !!!!
    ...


def onStatusChange(callback: Callable[[LayerEnum, str], None]):
    """
    Configure an action when the Status have changed.

    def callback(layer: LayerEnum, newStatus: str):

    """
    pass


def disconnect():
    pass


def close():
    """."""
    # Disconnect
    pass


# def getStatus() -> Status:
#     """."""
#     pass
