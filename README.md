Wappsto IoT
===============================================================================
[![versions](https://img.shields.io/pypi/pyversions/wappstoiot.svg)](https://github.com/wappsto/python-wappsto-iot)
[![Test Status](https://github.com/Wappsto/python-wappsto-iot/actions/workflows/test.yml/badge.svg)](https://github.com/Wappsto/python-wappsto-iot/actions/workflows/test.yml)
[![Lint Status](https://github.com/Wappsto/python-wappsto-iot/actions/workflows/lint.yml/badge.svg)](https://github.com/Wappsto/python-wappsto-iot/actions/workflows/lint.yml)
[![Coverage](https://codecov.io/github/wappsto/python-wappsto-iot/branch/main/graph/badge.svg)](https://codecov.io/github/wappsto/python-wappsto-iot)
[![pypi](https://img.shields.io/pypi/v/wappstoiot.svg)](https://pypi.python.org/pypi/wappstoiot)
[![license](https://img.shields.io/github/license/wappsto/python-wappsto-iot.svg)](https://github.com/wappsto/python-wappsto-iot/blob/main/LICENSE)
[![SeluxitA/S](https://img.shields.io/badge/Seluxit_A/S-1f324d.svg?logo=data:image/x-icon;base64,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)](https://seluxit.com)
[![Wappsto](https://img.shields.io/badge/Wappsto-1f324d.svg?logo=data:image/x-icon;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAACXBIWXMAAAEuAAABLgF7cRpNAAAEM0lEQVR4nO1bwY3bMBCcyysBEpw6sDo4P4LgflEHUQm6DlyCSrgOTiU43yAPpgOVoOtATh55bh6iHJm3uyJFOQxwGmCB2CR3h0tyuVxfbogIrxlvUhNIjc0BqQmkxuaA1ARSY3NAagKpsTkgNYHU2BwgfF8BOAIgRloABwD59el5I8fAqQXP+YhhTi9BRFPZE1FL/miIKHN0/EvJLAdftHaOZx3u5PsAZSN6V+k/klX4jsryhcqmqALIx0oVybWnYc5nB4RsIw0l/f+TH9EQEW6I6C2A30Jw+QqgAdDbz4UNJjuh/8n2af3jVxD2AAyAW6H9GQNfYz9nGPh+Efq/G7c/h1pZhaPi2WvFhLkzfyQ5INfCmBxEVAiNMVuxU8gskbkY5RN/OBQxiVAD4EFo29ltmEXoH5FhuMelbf9guSwDEd0L3vFdwUdlZY6RKw/S8xLtmE4lE8bfazEgJKI3Cslm4cTX1FsKOnLtfDwGkjUKWZ8z6spB0RfqVGmXQiPfBRrJSN+uRYCuStHTUniA7Rg9ZuoAydt5oKGc5Gjtez1q1123YPK5oOtAROfXoBFiZBEYUzs75sS03WKI5trNkEFOdE4ASvxNynxRCN8bABePIc7roWfNZwsbZdxaR2gqDaOrH9unHbnsrqdlRrVjRcQ7liM6oorgwS3s+Xr2WbWYtNZ3UmtG/Kns52x7B4sImdvWhdKuHZeYXZiPfdwB3RVIZCRH9V9E9FNoW3LduWIYvd20j/sWODLR8nNg1HXRQ74Z3gP4wHx/wvCMDY34LjjuF3N0HWAERWUkkbGQ6osK8TUFibO5+MRsGw6habEktaB/inolW2L6O5VF5yZSvimT/76iHa94xtUDuDiwwzq/A2QAPintH7FODSEHX7Z7MTfOAUZQWiymc6lbKmzAtkn2Q1Ao9i/AOaAFH7FjA2ED4M6j3x1iKjwDOK4ncIFVOD8Nc35i0uJKOfcSqgh73u8aqSZomO9uMZSlQ7EH8CS0/bDC4SnCHnfMDNc5xAFA+DEYn7ccnq2+0v5b4hEaFP3u/xHKNuJy+DZwK0rvALc4ohVB1rAp6tAUSYmEb37OxZER3PnW4gR7fhmRqr9iIqcpKwRlPtVibTJaVqmV2H2ComS3kMbMKeQwtxqS44j8XpZGGS9OhPRdJ46ZI8NViTql/xoFzYz4NJZovrDKjVN/nJn7aYyLnDvwmVaJdQqave0rFVYN+EhfgE9/jWptZjVyZSUONGzJmvRtS7QsqdHiCFmbteVwIHnn5ZodHyJzk5tD7WFDkjrS9mzM8SFRRBBoPPTPSRNhv5jTf00SaxVRQPr1KMHL+dcg0dF1/laoJPl2cOHt/FASOQ2edYn0NFw31RUm7kplbblBr7Pc8hB9N0Tbf5p61dgckJpAamwOSE0gNTYHpCaQGpsDUhNIjVfvgD9WFsGCdX/VsgAAAABJRU5ErkJggg==)](https://wappsto.com)

The wappstoiot module provide a simple python interface to [wappsto.com](https://wappsto.com/) for easy prototyping.


## Prerequisites

A [wappsto.com](https://wappsto.com/) Account, that the unit can connect to.

The wappsto module requires a set of certificates for authentication. The certificates can be downloaded from [wappsto.com](https://wappsto.com/), or with the build-in CLI tool: `python3 -m wappstoiot`.
The certificates provides the unit with the secure connection to wappsto.com.

To read more about how the Wappsto IoT inner workings, go [here](https://documentation.wappsto.com).

## The Basics

To understand how to use Wappsto IoT, there is some terms that need to be known.
* Control
    - Change request value.
* Report
    - The current value.
* Refresh
    - Value Update request.
* Delete
    - inform that a delete have happened.
* Network
    - contains Devices
* Devices
    - Contains Values

Wappsto IoT are using the python [logging library](https://docs.python.org/3/library/logging.html) for logging out the errors, warnings and debuging info. If comthing do not work as you expected, this will be a good place to start.

Wappsto IoT are also using docstring, so the build-in [help function](https://docs.python.org/3/library/functions.html#help) which will print a help page of the given function passed in.

For ease of use of the library, the names of device and values are used as a identifier, to link them to the ones found in you network on wappsto. Which means that you can not have two Devices of same name, or two value of same name under the same device.


## Installation using pip

The wappsto module can be installed using PIP (Python Package Index) as follows:

```bash
$ pip install -U wappstoiot
```


Working examples of usage can be found in the [example folder](./example).

The needed certificates can be downloaded with [IoT Certificate Manager](https://wappsto.com/store/application/iot_certificate_manager).
Where path is the path to the config-folder, given in the following code example.


### Echo example

The following explains the example code found in [echo.py](./example/echo.py).


```python
wappstoiot.config(
    config_folder="echo"
)
```
The `config` function is setting up the folder for where Wappsto IoT are looking for the `ca.crt`, `client.key` and a `client.crt` files, which is used to connect to Wappsto.


```python
network = wappstoiot.createNetwork(
    name="echo",
)
```
Set the displayed name of the network, and return the created network.


```python
device = network.createDevice(
    name="EchoDevice"
)
```
Set the displayed name of the device, under the given network that have been named: `echo`.


```python
value = device.createValue(
    name="Moeller",
    permission=wappstoiot.PermissionType.READWRITE,
    value_template=wappstoiot.ValueTemplate.STRING
)
```
Set the displayed name of the value, under the given device that have been named: `EchoDevice`.

It also set what the permission types of that value should be. Here it is set to both read & write. The naming is from the wappsto side. So read permission means that Wappsto can recreive a report from the device. A Write permission means that Wappsto can send a control value to the device.

Value template is set to be STRING, which inform wappsto, that the value will be of type string, with a max length of 64 charactor. The templates are used to avoid to setup the value yourself. If a custom String value are needed, look at method: `createStringValue` insread.


```python
value.onControl(
    callback=lambda obj, new_value: obj.report(new_value)
)
```
Since the value permission include a write, is it needed to setup a control function, that are called when a control value are received. The function gets the value object in (obj), and the new target value (new_value) as parameters. The new value parameter neither a string or a float, since this is set as a STRING, the parameter will also be a string. In this example it just report back the value, which it can because it also have the read permission. The control function is then passed to the onControl method.
Note that onControl can also be used as a function decorator.
The control function should not be a blocking function.

```python
value.onRefresh(
    callback=lambda obj: obj.report(f"{obj.data} Refreshed!")
)
```
Since the value permission include a read, it is also possiable to request a update of the value. If this is behavier is wanted a refresh function need to be setup, which iscall when a refresh request is received. The function gets the value object in (obj). In this example it just report back the value with ` Refreshed!` append, which it can because it also have the read permission. The refresh function is then passed to the onRefresh method.
Note that onRefresh can also be used as a function decorator.
The refresh function should not be a blocking function.


```python
try:
    while True:
        time.sleep(0.5)
except KeyboardInterrupt:
    pass
finally:
    wappstoiot.close()
```
With everything setup wappstoiot is non blocking. Which allowes the execution of other things.
Here there isn't there anything else to be executed, so that is setup a buzzy loop to prevent the program exiting.
When the user hits `ctrl+c`, it stop the while-loop, and closes the wappsto connection.

## Help Documentation.

### wappstoiot.config
```python
config(
    config_folder: Union[pathlib.Path, str] = '.',
    connection: wappstoiot.ConnectionTypes = <ConnectionTypes.IOTAPI: 'jsonrpc'>,
    fast_send: bool = True,
    ping_pong_period_sec: Optional[int] = None,
    offline_storage: Union[wappstoiot.utils.offline_storage.OfflineStorage, bool] = False,
    rpc_timeout_sec: int = 3,
    max_reconnect_retry_count: Optional[int] = None
) -> None
```
Configure the WappstoIoT settings.

This function call is optional.
If it is not called, the default settings will be used for WappstoIoT.
This function will also connect to the WappstoIoT API on call.
In the cases that this function is not called, the connection will be
make when an action is make that requests the connection.

Args:
    config_folder: The folder where it should find the certificate files.
    fast_send: whether or not it should wait for the sent message to be parsed.
    ping_pong_period_sec: The period for a ping package to be sent.
    offline_storage: If it should store value that failed in been sent.
    rpc_timeout_sec: The timeout for a sent RPC package.
    max_reconnect_retry_count: How many times it should try reconnect before throw an exception.


### wappstoiot.PermissionType

```python
class ValueTemplate(builtins.str, enum.Enum):
```
All possible Value Permission Types.

 - NONE
 - READ
 - WRITE
 - READWRITE / WRITEREAD

### wappstoiot.ValueTemplate
```python
class ValueTemplate(builtins.str, enum.Enum):
```
Predefined ValueTemplate.
Each of the predefined ValueTemplate, have default
value parameters set, which include BaseType, name,
permission, range, step and the unit.

Avaliable Value Templates:
 - ADDRESS_NAME
 - ALTITUDE_M
 - ANGLE
 - APPARENT_POWER_VA
 - BLOB
 - BOOLEAN_ONOFF
 - BOOLEAN_TRUEFALSE
 - CITY
 - CO2_PPM
 - COLOR_HEX
 - COLOR_INT
 - COLOR_TEMPERATURE
 - CONCENTRATION_PPM
 - CONNECTION_STATUS
 - COUNT
 - COUNTRY
 - COUNTRY_CODE
 - CURRENT_A
 - DISTANCE_M
 - DURATION_MIN
 - DURATION_MSEC
 - DURATION_SEC
 - EMAIL
 - ENERGY_KWH
 - ENERGY_MWH
 - ENERGY_PRICE_DKK_KWH
 - ENERGY_PRICE_DKK_MWH
 - ENERGY_PRICE_EUR_KWH
 - ENERGY_PRICE_EUR_MWH
 - ENERGY_WH
 - FREQUENCY_HZ
 - HUMIDITY
 - IDENTIFIER
 - IMAGE_JPG
 - IMAGE_PNG
 - IMPULSE_KWH
 - INTEGER
 - JSON
 - LATITUDE
 - LOAD_CURVE_ENERGY_KWH
 - LOAD_CURVE_ENERGY_MWH
 - LOAD_CURVE_ENERGY_WH
 - LONGITUDE
 - LUMINOSITY_LX
 - NUMBER
 - ORGANIZATION
 - PERCENTAGE
 - PHONE
 - POSTCODE
 - POWER_KW
 - POWER_WATT
 - PRECIPITATION_MM
 - PRESSURE_HPA
 - REACTIVE_ENERGY_KVARH
 - REACTIVE_POWER_KVAR
 - SPEED_KMH
 - SPEED_MS
 - STREET
 - STRING
 - TEMPERATURE_CELSIUS
 - TEMPERATURE_FAHRENHEIT
 - TEMPERATURE_KELVIN
 - TIMESTAMP
 - TIME_OF_DAY
 - TOTAL_ENERGY_KWH
 - TOTAL_ENERGY_MWH
 - TOTAL_ENERGY_WH
 - TRIGGER
 - UNIT_TIME
 - VOLTAGE_V
 - VOLUME_M3
 - XML


### wappstoiot.onStatusChange
```python
def onStatusChange(
    StatusID: Union[service.StatusID, connection.StatusID],
    callback: Callable[[Union[service.StatusID, connection.StatusID], Any], None]
) -> None:
```
Configure an action when the Status have changed.

### wappstoiot.service.StatusID
```python
class StatusID(builtins.str, enum.Enum):
```
The different states the service class can be in.

service Status IDs:
 - ERROR
 - IDLE
 - SEND
 - SENDERROR
 - SENDING

### wappstoiot.connection.StatusID
```python
class StatusID(builtins.str, enum.Enum):
```
The difference connection Statuses.

Connection Status IDs:
 - CONNECTED
 - CONNECTING
 - DISCONNECTING
 - DISCONNETCED

### wappstoiot.createNetwork
```python
def createNetwork(
    name: str,
    description: str = "",
) -> Network:
```
Create a new Wappsto Network.

A Wappsto Network is references to the main grouping, of which multiple
device are connected.

### wappstoiot.Network
```python
class Network(builtins.object):
    name: str
    uuid: uuid.UUID
```

```python
    def cancelOnChange(self) -> None:
```
Cancel the callback set in onChange-method.

```python
    def cancelOnCreate(self) -> None:
```
Cancel the callback set in onCreate-method.

```python
    def cancelOnDelete(self) -> None:
```
Cancel the callback set in onDelete-method.


```python
    def close(self) -> None:
```
Stop all the internal and children logic.

```python
    def delete(self) -> None:
```
Prompt a factory reset.
Normally it is used to unclaim a Network & delete all children.
This means that manufacturer and owner will be reset (or not),
in relation of the rules set up in the certificates.
```python
    def onChange(
        self,
        callback: Callable[[ForwardRef('Network')], NoneType]
    ) -> Callable[[ForwardRef('Network')], NoneType]:
```
Configure a callback for when a change to the Network have occurred.

```python
    def onCreate(
        self,
        callback: Callable[[ForwardRef('Network')], NoneType]
    ) -> Callable[[ForwardRef('Network')], NoneType]:
```
Configure a callback for when a create have been make for the Device.
```python
    def onDelete(
        self,
        callback: Callable[[ForwardRef('Network')], NoneType]
    ) -> Callable[[ForwardRef('Network')], NoneType]
```
Configure an action when a Delete Network have been Requested.

Normally when a Delete have been requested on a Network,
it is when it is not wanted anymore, and the Network have been
unclaimed. Which mean that all the devices & value have to be
recreated, and/or the program have to close.


```python
    def createDevice(
        self,
        name: str,
        manufacturer: Optional[str] = None,
        product: Optional[str] = None,
        version: Optional[str] = None,
        serial: Optional[str] = None,
        protocol: Optional[str] = None,
        communication: Optional[str] = None,
        description: Optional[str] = None,
    ) -> wappstoiot.modules.device.Device:
```
Create a new Wappsto Device.
A Wappsto Device is references something that is attached to the network
that can be controlled or have values that can be reported to Wappsto.
This could be a button that is connected to this unit,
or in the case of this unit is a gateway, it could be a remote unit.

### wappstoiot.Device

```python
class Device:
    name: str
    uuid: uuid.UUID
```

```python
    def onDelete(
        self,
        callback: Callable[['Device'], None],
    ) -> Callable[['Device'], None]:
```
Configure an action when a Delete on this Device have been Requested.

Normally when a Delete have been requested,
it is when it is not wanted anymore.
Which mean that all the device and it's values have to be removed,
and the process of setting up the device, should be executed again.
This could result in the same device are created again, or if the
device was not found, it will just be removed.

```python
    def cancelOnDelete(self) -> None:
```
Cancel the callback set in onDelete-method.

```python
    def onChange(
        self,
        callback: Callable[['Device'], None],
    ) -> Callable[['Device'], None]:
```
Configure a callback for when a change to the Device have occurred.

```python
    def cancelOnChange(self) -> None:
```
Cancel the callback set in onChange-method.

```python
    def onCreate(
        self,
        callback: Callable[['Device'], None],
    ) -> Callable[['Device'], None]:
```
Configure a callback for when a request have been make for the Value.

```python
    def cancelOnCreate(self) -> None:
```
Cancel the callback set in onCreate-method.

```python
    def delete(self) -> None:
```
Request a delete of the Device, & all it's Children.

```python
    def close(self) -> None:
```
Stop all the internal and children logic.

```python
    def createNumberValue(
        self,
        name: str,
        *,
        permission: PermissionType,
        type: str,
        min: Union[int, float],
        max: Union[int, float],
        step: Union[int, float],
        unit: str,
        description: Optional[str] = None,
        si_conversion: Optional[str] = None,
        period: Optional[int] = None,  # in Sec
        delta: Optional[Union[int, float]] = None,
        mapping: Optional[Dict[str, str]] = None,
        meaningful_zero: Optional[bool] = None,
        ordered_mapping: Optional[bool] = None,
    ) -> Value:
```
Create a Wappsto Number Value.

A Wappsto Value is where the changing data can be found & are handled.

This require you to setup manually, what `createValue`
with `value_template` setup for you.

Args:
    name: The displayed name on Wappsto.
    permission: Whether or not wappsto can read and/or write to the client.
    type: The displayed value on Wappsto.
    min: The displayed min on Wappsto.
    max: The displayed max on Wappsto.
    step: The displayed step on Wappsto.
    unit: The displayed unit on Wappsto. Ex: KW, m/s, hPa or m²
    description: The description of the value.
    si_conversion: Conversion algorithm from unit to a SI unit.
        Example for Wh to J: [J] = 3600 * [Wh]
    mapping: How the value should be displayed on Wappsto.
        Example: The mapping: {'0': 'false', '1': 'true'}, will on wappsto
            show 0 as false & 1 as true. But the value will still be 0 or 1.
    meaningful_zero: Whether or not a zero is truly nothing.
    ordered_mapping: Whether or not the order in the mapping matter.
    period: The time between forced update. the trigger is every
        multiplex from 00:00 o' clock.
        (Uses the callback set in onRefresh to force a update.)
        (Can be overwritten by Wappsto)
    delta: The change that need to happen before the value are updated
        and sent to wappsto.
        (Period & refresh request overwrites this)
        (Can be overwritten by Wappsto)

```python
    def createStringValue(
        self,
        name: str,
        *,
        permission: PermissionType,
        type: str,
        max: Union[int, float],
        encoding: Optional[str] = None,
        description: Optional[str] = None,
        period: Optional[int] = None,
    ) -> Value:
```
Create a Wappsto String Value.

A Wappsto Value is where the changing data can be found & are handled.

This require you to setup manually, what `createValue`
with `value_template` setup for you.

Args:
    name: The displayed name on Wappsto.
    permission: Whether or not wappsto can read and/or write to the client.
    type: The displayed string on Wappsto.
    max: The displayed max size on Wappsto.
    encoding: the encoding type of the data.
        Used to display the data correctly on wappsto.
    description: The description of the value.
    period: The time between forced update. the trigger is every
        multiplex from 00:00 o' clock.
        (Uses the callback set in onRefresh to force a update.)
        (Can be overwritten by Wappsto)

```python
    def createBlobValue(
        self,
        name: str,
        *,
        permission: PermissionType,
        type: str,
        max: Union[int, float],
        encoding: Optional[str] = None,
        description: Optional[str] = None,
        period: Optional[int] = None,
    ) -> Value:
```
Create a Wappsto BLOB Value.

A Wappsto Value is where the changing data can be found & are handled.

This require you to setup manually, what `createValue`
with `value_template` setup for you.

Args:
    name: The displayed name on Wappsto.
    permission: Whether or not wappsto can read and/or write to the client.
    type: The displayed string on Wappsto.
    max: The displayed max size on Wappsto.
    encoding: the encoding type of the data.
        Used to display the data correctly on wappsto.
    description: The description of the value.
    period: The time between forced update. the trigger is every
        multiplex from 00:00 o' clock.
        (Uses the callback set in onRefresh to force a update.)
        (Can be overwritten by Wappsto)

```python
    def createXmlValue(
        self,
        name: str,
        *,
        permission: PermissionType,
        type: str,
        xsd: Optional[str] = None,
        namespace: Optional[str] = None,
        description: Optional[str] = None,
        period: Optional[int] = None,
    ) -> Value:
```
Create a Wappsto XML Value.

A Wappsto Value is where the changing data can be found & are handled.

This require you to setup manually, what `createValue`
with `value_template` setup for you.

Args:
    name: The displayed name on Wappsto.
    permission: Whether or not wappsto can read and/or write to the client.
    type: The displayed string on Wappsto.
    xsd: The XMLs Schema definition.
    namespace: The XMLNamespace for the data.
    description: The description of the value.
    period: The time between forced update. the trigger is every
        multiplex from 00:00 o' clock.
        (Uses the callback set in onRefresh to force a update.)
        (Can be overwritten by Wappsto)

```python
    def createValue(
        self,
        name: str,
        permission: PermissionType,
        value_template: ValueTemplate,
        description: Optional[str] = None,
        period: Optional[int] = None,
        delta: Optional[Union[int, float]] = None,
    ) -> Value:
```

Create a Wappsto Value.

A Wappsto Value is where the changing data can be found & are handled.

If a value_template have been set, that means that the parameters like:
name, permission, min, max, step, encoding & unit have been set
for you, to be the right settings for the given type. But you can
still change it, if you choose sow.

It no ValueTemplate fits you need, take a look at:
createNumberValue, createStringValue, createBlobValue or createXmlValue

Args:
    name: The displayed name on Wappsto.
    permission: Whether or not wappsto can read and/or write to the client.
    value_template: Contain pre-make config parameters. That is ensured
        to work well with Wappsto. Want something else?
        Use createNumberValue, createStringValue or createBlobValue.
    description: The description of the value.
    period: The time between forced update. the trigger is every
        multiplex from 00:00 o' clock. (Can be overwritten by Wappsto)
        (Uses the callback set in onRefresh to force a update.)
    delta: The change that need to happen before the value are updated
        and sent to wappsto.
        (Period & refresh request overwrites this)
        (Can be overwritten by Wappsto)


### wappstoiot.Value
```python
class Value:
    name: str
    uuid. uuid.UUID
```

```python
    def getControlData(self) -> Optional[Union[float, str]]:
```
Return the last Control value.

The returned value will be the last Control value,
unless there isn't one, then it will return None.

```python
    def getControlTimestamp(self) -> Optional[datetime]:
```
Return the timestamp for when last Control value was updated.

The returned timestamp will be the last time Control value was updated,
unless there isn't one, then it will return None.

```python
    def getReportData(self) -> Optional[Union[float, str]]:
```
Return the last Report value.

The returned value will be the last Report value.
unless there isn't one, then it will return None.

```python
    def getReportTimestamp(self) -> Optional[datetime]:
```
Return the timestamp for when last Report value was updated.

The returned timestamp will be the last time Control value was updated,
unless there isn't one, then it will return None.

```python
    def onChange(
        self,
        callback: Callable[['Value'], None],
    ) -> Callable[['Value'], None]:
```
Add a trigger on when change have been make.

A change on the Value typically will mean that a parameter, like
period or delta or report value have been changed,
from the server/user side.

Callback:
    ValueObj: The Object that have had a change to it.
    ChangeType: Name of what have change in the object.

```python
    def cancelOnChange(self) -> None:
```
Cancel the callback set in onChange-method.

```python
    def onReport(
        self,
        callback: Callable[['Value', Union[str, float]], None],
    ) -> Callable[['Value', Union[str, float]], None]:
```
Add a trigger on when Report data change have been make.

This trigger even if the Report data was changed to the same value.

Callback:
    Value: the Object that have had a Report for.
    Union[str, int, float]: The Value of the Report change.

```python
    def cancelOnReport(self) -> None:
```
Cancel the callback set in onReport-method.
```python
    def onControl(
        self,
        callback: Callable[['Value', Union[str, float]], None],
    ) -> Callable[['Value', Union[str, float]], None]:
```
Add trigger for when a Control request have been make.

A Control value is typical use to request a new target value,
for the given value.

Callback:
    ValueObj: This object that have had a request for.
    any: The Data.

```python
    def cancelOnControl(self) -> None:
```
Cancel the callback set in onControl-method.

```python
    def onCreate(
        self,
        callback: Callable[['Value'], None],
    ) -> Callable[['Value'], None]:
```
Add trigger for when a state was created.

A Create is typical use to create a new state.

Callback:
    ValueObj: This object that have had a refresh request for.

```python
    def cancelOnCreate(self) -> None:
```
Cancel the callback set in onCreate-method.

```python
    def onRefresh(
        self,
        callback: Callable[['Value'], None],
    ) -> Callable[['Value'], None]:
```
Add trigger for when a Refresh where requested.

A Refresh is typical use to request a update of the report value,
in case of the natural update cycle is not fast enough for the user,
or a extra sample are wanted at that given time.

Callback:
    ValueObj: This object that have had a refresh request for.

```python
    def cancelOnRefresh(self) -> None:
```
Cancel the callback set in onRefresh-method.

```python
    def onDelete(
        self,
        callback: Callable[['Value'], None],
    ) -> Callable[['Value'], None]:
```
For when a 'DELETE' request have been called on this element.

```python
    def cancelOnDelete(self) -> None:
```
Cancel the callback set in onDelete-method.

```python
    def delete(self) -> None:
```
Request a delete of the Device, & all it's Children.

```python
    def report(
        self,
        value: Union[int, float, str, LogValue, List[LogValue], None],
        timestamp: Optional[datetime] = None,
        *,
        force: bool = False,
        add_jitter: bool = False,
    ) -> None:
```

Report the new current value to Wappsto.

The Report value is typical a measured value from a sensor,
whether it is a GPIO pin, an analog temperature sensor or a
device over a I2C bus.

```python
    def control(
        self,
        value: Union[int, float, str, None],
        timestamp: Optional[datetime] = None
    ) -> None:
```
Report the a new control value to Wappsto.

A Control value is typical only changed if a target wanted value,
have changed, whether it is because of an on device user controller,
or the target was outside a given range.

```python
    def close(self) -> None:
```
Stop all the internal logic.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE.md](LICENSE.md) file for details.

