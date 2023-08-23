"""Contain the Value Object."""
import uuid
import logging

from enum import Enum
from datetime import datetime

from typing import Any
from typing import Callable
from typing import cast
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from ..service.template import ServiceClass
# from .template import dict_diff
from .template import ValueBaseType
# from .template import valueSettings
from ..schema import base_schema as WSchema
from ..schema.base_schema import PermissionType
from ..schema.base_schema import LogValue
from ..schema.iot_schema import WappstoMethod

from ..utils.Timestamp import str_to_datetime

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    # NOTE: To avoid ciclic import
    from .device import Device

# #############################################################################
#                                 Value Setup
# #############################################################################


class Period(str, Enum):
    """Different Period options."""
    PERIODIC_REFRESH = "periodic"
    DROP_UNTIL = "drop"


class Delta(str, Enum):
    """Different Delta options."""
    ONLY_UPDATE_IF = ""
    EXTRA_UPDATES = ""


class Value:
    """
    A value is used to describe each possible values for a specific device.

    A value can assign some limit to the states: as min, max or steps.
    """

    class RequestType(str, Enum):
        """All the different Request types possible for a Value."""

        refresh = "refresh"
        control = "control"
        delete = "delete"

    class ChangeType(str, Enum):
        """All the different Change types possible for a Value."""

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

    __value_type_2_Schema = {
        ValueBaseType.STRING: WSchema.StringValue,
        ValueBaseType.NUMBER: WSchema.NumberValue,
        ValueBaseType.BLOB: WSchema.BlobValue,
        ValueBaseType.XML: WSchema.XmlValue,
    }

    def __init__(
        self,
        parent: 'Device',
        value_type: ValueBaseType,
        name: str,
        value_uuid: Optional[uuid.UUID],  # Only used on loading.
        type: Optional[str] = None,
        permission: PermissionType = PermissionType.READWRITE,
        min: Optional[str] = None,
        max: Optional[str] = None,
        step: Optional[str] = None,
        encoding: Optional[str] = None,
        xsd: Optional[str] = None,
        namespace: Optional[str] = None,
        period: Optional[int] = None,  # in Sec
        delta: Optional[Union[int, float]] = None,
        description: Optional[str] = None,
        meaningful_zero: Optional[bool] = None,
        mapping: Optional[Dict[str, str]] = None,
        ordered_mapping: Optional[bool] = None,
        si_conversion: Optional[str] = None,
        unit: Optional[str] = None,
    ):
        """Configure the Value settings."""
        self.log = logging.getLogger(__name__)
        self.log.addHandler(logging.NullHandler())

        self.value_type = value_type

        self.__callbacks: Dict[
            str,
            Union[
                Callable[[WSchema.ValueUnion, WappstoMethod], None],
                Callable[[WSchema.State, WappstoMethod], None],
            ]
        ] = {}

        self.schema = self.__value_type_2_Schema[value_type]
        self.report_state: WSchema.State
        self.control_state: WSchema.State
        self.parent = parent
        self.element: Union[
            WSchema.StringValue,
            WSchema.NumberValue,
            WSchema.BlobValue,
            WSchema.XmlValue
        ] = self.schema()

        self.children_name_mapping: Dict[WSchema.StateType, uuid.UUID] = {}

        self.connection: ServiceClass = parent.connection

        subValue = self.__parseValueTemplate(
            ValueBaseType=value_type,
            encoding=encoding,
            mapping=mapping,
            max_range=max,
            meaningful_zero=meaningful_zero,
            min_range=min,
            namespace=namespace,
            ordered_mapping=ordered_mapping,
            si_conversion=si_conversion,
            step=step,
            unit=unit,
            xsd=xsd,
        )

        element = self.connection.get_value(value_uuid) if value_uuid else None

        self.__uuid: uuid.UUID = value_uuid if value_uuid else uuid.uuid4()

        self.element = self.schema(
            name=name,
            description=description,
            period=period,
            delta=delta,
            type=type,
            permission=permission,
            **subValue,
            meta=WSchema.ValueMeta(
                version=WSchema.WappstoVersion.V2_0,
                type=WSchema.ValueMeta.WappstoMetaType.VALUE,
                id=self.uuid
            )
        )

        if element:
            self.__update_self(element)
            # self.__print(element)
            if self.element != element:
                # TODO: Post diff only.
                self.log.info("Data Models Differ. Sending Local.")
                self.connection.post_value(
                    device_uuid=self.parent.uuid,
                    data=self.element
                )
            self.__update_state()
        else:
            self.connection.post_value(
                device_uuid=self.parent.uuid,
                data=self.element
            )

            self._createStates(permission)

    # def __print(self, element):
    #     self.log.debug(
    #         type(self.element)
    #     )
    #     self.log.debug(
    #         self.element
    #     )
    #     self.log.debug(
    #         type(element)
    #     )
    #     self.log.debug(
    #         element
    #     )

    def getControlData(self) -> Optional[Union[float, str]]:
        """
        Returns the last Control value.

        The returned value will be the last Control value,
        unless there isn't one, then it will return None.
        """
        if self.value_type == ValueBaseType.NUMBER:
            if self.control_state.data == "NA":
                return None
            return float(self.control_state.data)
        return self.control_state.data

    def getControlTimestamp(self) -> Optional[datetime]:
        """
        Returns the timestamp for when last Control value was updated.

        The returned timestamp will be the last time Control value was updated,
        unless there isn't one, then it will return None.
        """
        if isinstance(self.control_state.timestamp, datetime):
            return self.control_state.timestamp
        return None

    def getReportData(self) -> Optional[Union[float, str]]:
        """
        Returns the last Report value.

        The returned value will be the last Report value.
        unless there isn't one, then it will return None.
        """
        if self.value_type == ValueBaseType.NUMBER:
            if self.report_state.data == "NA":
                return None
            return float(self.report_state.data)
        return self.report_state.data

    def getReportTimestamp(self) -> Optional[datetime]:
        """
        Returns the timestamp for when last Report value was updated.

        The returned timestamp will be the last time Control value was updated,
        unless there isn't one, then it will return None.
        """
        if isinstance(self.report_state.timestamp, datetime):
            return self.report_state.timestamp
        return None

    @property
    def name(self) -> str:
        """Returns the name of the value."""
        return cast(str, self.element.name)

    @property
    def uuid(self) -> uuid.UUID:
        """Returns the uuid of the value."""
        return self.__uuid

    # -------------------------------------------------------------------------
    #   Helper methods
    # -------------------------------------------------------------------------

    def __argumentCountCheck(self, callback: Callable, requiredArgumentCount: int) -> bool:
        """Check if the requeried Argument count for given function fits."""
        allArgument: int = callback.__code__.co_argcount
        the_default_count: int = len(callback.__defaults__) if callback.__defaults__ is not None else 1
        mandatoryArguments: int = callback.__code__.co_argcount - the_default_count
        return (
            requiredArgumentCount <= allArgument and requiredArgumentCount >= mandatoryArguments
        )

    def __parseValueTemplate(
        self,
        ValueBaseType: ValueBaseType,
        max_range: str,
        min_range: Optional[str] = None,
        step: Optional[float] = None,
        encoding: Optional[str] = None,
        mapping: Optional[Dict[str, Any]] = None,
        meaningful_zero: Optional[bool] = None,
        namespace: Optional[str] = None,
        ordered_mapping: Optional[bool] = None,
        si_conversion: Optional[str] = None,
        unit: Optional[str] = None,
        xsd: Optional[str] = None,
    ) -> Dict[
        str,
        Union[WSchema.Number, WSchema.Blob, WSchema.String, WSchema.Xml]
    ]:
        subValue: Dict[
            str,
            Union[WSchema.Number, WSchema.Blob, WSchema.String, WSchema.Xml]
        ]

        if ValueBaseType == ValueBaseType.NUMBER:
            subValue = {
                "number": WSchema.Number(
                    min=cast(str, min_range),
                    max=max_range,
                    step=cast(str, step),
                    mapping=mapping,
                    meaningful_zero=meaningful_zero,
                    ordered_mapping=ordered_mapping,
                    si_conversion=si_conversion,
                    unit=unit,
                )
            }
        elif ValueBaseType == ValueBaseType.XML:
            subValue = {
                "xml": WSchema.Xml(
                    xsd=xsd,
                    namespace=namespace,
                )
            }
        elif ValueBaseType == ValueBaseType.STRING:
            subValue = {
                "string": WSchema.String(
                    max=max_range,
                    encoding=encoding
                )
            }
        elif ValueBaseType == ValueBaseType.BLOB:
            subValue = {
                "blob": WSchema.Blob(
                    max=max_range,
                    encoding=encoding
                )
            }

        return subValue

    def __update_self(self, element: WSchema.Value) -> None:
        new_elem = self.element.model_dump(exclude_none=True)
        old_elem = element.model_dump(exclude_none=True)

        if type(self.element) is type(element):
            new_model = cast(type(element), element.model_copy(update=new_elem))
            new_model.meta = element.meta.model_copy(update=new_model.meta)

            self.element = new_model

            if isinstance(element, WSchema.NumberValue):
                new_model.number = element.number.model_copy(
                    update=new_model.number
                )
            elif isinstance(element, WSchema.StringValue):
                new_model.string = element.string.model_copy(
                    update=new_model.string
                )
            elif isinstance(element, WSchema.BlobValue):
                new_model.blob = element.blob.model_copy(
                    update=new_model.blob
                )
            elif isinstance(element, WSchema.XmlValue):
                new_model.xml = element.xml.model_copy(
                    update=new_model.xml
                )
        else:
            if isinstance(element, WSchema.StringValue):
                old_elem.pop('string')
            elif isinstance(element, WSchema.NumberValue):
                old_elem.pop('number')
            elif isinstance(element, WSchema.BlobValue):
                old_elem.pop('blob')
            elif isinstance(element, WSchema.XmlValue):
                old_elem.pop('xml')

            old_dict = self.schema(**old_elem)
            new_model = old_dict.model_copy(update=new_elem)

            new_model.meta = element.meta.model_copy(
                update=element.meta.model_dump(exclude_none=True)
            )

            self.log.debug(f"CC: {new_model}")
            self.element = new_model

        # TODO: Check for the Difference Value-types & ensure that it is right.

    def __update_state(self) -> None:
        state_count = len(self.element.state)
        if self.element.permission == PermissionType.NONE:
            return
        elif self.element.permission is None:
            return
        elif state_count == 0 or self.element.state is None:
            self._createStates(self.element.permission)
            return

        state_uuid = self.element.state[0]
        state_obj = self.connection.get_state(uuid=state_uuid)
        self.log.info(f"Found State: {state_uuid} for device: {self.uuid}")
        self.children_name_mapping[state_obj.type] = state_uuid

        if not state_obj:
            return

        if state_obj.type == WSchema.StateType.REPORT:
            self.report_state = state_obj
        elif state_obj.type == WSchema.StateType.CONTROL:
            self.control_state = state_obj

        if state_count == 1:
            if self.element.permission not in [PermissionType.READ, PermissionType.WRITE]:
                if state_obj.type == WSchema.StateType.REPORT:
                    self._createStates(PermissionType.WRITE)
                elif state_obj.type == WSchema.StateType.CONTROL:
                    self._createStates(PermissionType.READ)
            return

        state_uuid = self.element.state[1]
        state_obj = self.connection.get_state(uuid=state_uuid)
        self.log.info(f"Found State: {state_uuid} for device: {self.uuid}")
        self.children_name_mapping[state_obj.type] = state_uuid

        if state_obj.type == WSchema.StateType.REPORT:
            self.report_state = state_obj
        elif state_obj.type == WSchema.StateType.CONTROL:
            self.control_state = state_obj

    # def __update_state(self):
    #     for state_uuid in self.element.state:
    #         state_obj = self.connection.get_state(uuid=state_uuid)
    #         if state_obj:
    #             self.log.info(f"Found State: {state_uuid} for device: {self.uuid}")
    #             self.children_name_mapping[state_obj.type.name] = state_uuid
    #             if state_obj.type == WSchema.StateType.REPORT:
    #                 self.report_state = state_obj
    #             elif state_obj.type == WSchema.StateType.CONTROL:
    #                 self.control_state = state_obj

    # -------------------------------------------------------------------------
    #   Value 'on-' methods
    # -------------------------------------------------------------------------

    def onChange(
        self,
        callback: Callable[['Value'], None],
    ) -> Callable[['Value'], None]:
        """
        Add a trigger on when change have been make.

        A change on the Value typically will mean that a parameter, like
        period or delta or report value have been changed,
        from the server/user side.

        Callback:
            ValueObj: The Object that have had a change to it.
            ChangeType: Name of what have change in the object.
        """
        if not self.__argumentCountCheck(callback, 1):
            raise TypeError("The OnChange callback, is called with 1 argument.")

        def _cb(obj: WSchema.ValueUnion, method: WappstoMethod) -> None:
            try:
                if method in WappstoMethod.PUT:
                    callback(self)
            except Exception:
                self.log.exception("OnChange callback error.")
                raise

        self.__callbacks['onChange'] = _cb

        # UNSURE (MBK): on all state & value?
        self.connection.subscribe_value_event(
            uuid=self.uuid,
            callback=_cb
        )

        return callback

    def cancelOnChange(self) -> None:
        """Cancel the callback set in onChange-method."""
        self.connection.unsubscribe_value_event(
            uuid=self.uuid,
            callback=self.__callbacks['onChange']
        )

    def onReport(
        self,
        callback: Callable[['Value', Union[str, float]], None],
    ) -> Callable[['Value', Union[str, float]], None]:
        """
        Add a trigger on when Report data change have been make.

        This trigger even if the Report data was changed to the same value.

        Callback:
            Value: the Object that have had a Report for.
            Union[str, int, float]: The Value of the Report change.
        """
        if not self.__argumentCountCheck(callback, 2):
            raise TypeError("The OnReport callback, is called with 2 argument.")

        def _cb_float(obj: WSchema.State, method: WappstoMethod) -> None:
            try:
                if method == WappstoMethod.PUT:
                    callback(self, float(obj.data))
            except Exception:
                self.log.exception("onReport callback error.")
                raise

        def _cb_str(obj: WSchema.State, method: WappstoMethod) -> None:
            try:
                if method == WappstoMethod.PUT:
                    callback(self, obj.data)
            except Exception:
                self.log.exception("onReport callback error.")
                raise

        _cb = _cb_float if self.value_type == ValueBaseType.NUMBER else _cb_str

        self.__callbacks['onReport'] = _cb

        self.connection.subscribe_state_event(
            uuid=self.children_name_mapping[WSchema.StateType.REPORT],
            callback=_cb
        )

        return callback

    def cancelOnReport(self) -> None:
        """Cancel the callback set in onReport-method."""
        self.connection.unsubscribe_state_event(
            uuid=self.children_name_mapping[WSchema.StateType.REPORT],
            callback=cast(
                Callable[[WSchema.State, WappstoMethod], None],
                self.__callbacks['onReport'],
            )
        )

    def onControl(
        self,
        callback: Callable[['Value', Union[str, float]], None],
    ) -> Callable[['Value', Union[str, float]], None]:
        """
        Add trigger for when a Control request have been make.

        A Control value is typical use to request a new target value,
        for the given value.

        Callback:
            ValueObj: This object that have had a request for.
            any: The Data.
        """
        if not self.__argumentCountCheck(callback, 2):
            raise TypeError("The OnControl callback, is called with 2 argument.")

        def _cb_float(obj: WSchema.State, method: WappstoMethod) -> None:
            data: Union[float, str]
            try:
                if method == WappstoMethod.PUT:
                    try:
                        data = float(obj.data)
                    except ValueError:
                        data = obj.data
                    callback(self, data)
            except Exception:
                self.log.exception("OnChange callback error.")
                raise

        def _cb_str(obj: WSchema.State, method: WappstoMethod) -> None:
            try:
                if method == WappstoMethod.PUT:
                    callback(self, obj.data)
            except Exception:
                self.log.exception("onControl callback error.")
                raise

        _cb = _cb_float if self.value_type == ValueBaseType.NUMBER else _cb_str

        self.__callbacks['onControl'] = _cb

        self.connection.subscribe_state_event(
            uuid=self.children_name_mapping[WSchema.StateType.CONTROL],
            callback=_cb
        )

        return callback

    def cancelOnControl(self) -> None:
        """Cancel the callback set in onControl-method."""
        self.connection.unsubscribe_state_event(
            uuid=self.children_name_mapping[WSchema.StateType.CONTROL],
            callback=cast(
                Callable[[WSchema.State, WappstoMethod], None],
                self.__callbacks['onControl'],
            )
        )

    def onCreate(
        self,
        callback: Callable[['Value'], None],
    ) -> Callable[['Value'], None]:
        """
        Add trigger for when a state was created.

        A Create is typical use to create a new state.

        Callback:
            ValueObj: This object that have had a refresh request for.
        """
        if not self.__argumentCountCheck(callback, 1):
            raise TypeError("The onCreate callback, is called with 1 argument.")

        def _cb(obj: WSchema.State, method: WappstoMethod) -> None:
            try:
                if method == WappstoMethod.POST:
                    callback(self)
            except Exception:
                self.log.exception("onCreate callback error.")
                raise

        self.__callbacks['onCreate'] = _cb

        self.connection.subscribe_state_event(
            uuid=self.uuid,
            callback=_cb
        )

        return callback

    def cancelOnCreate(self) -> None:
        """Cancel the callback set in onCreate-method."""
        self.connection.unsubscribe_state_event(
            uuid=self.uuid,
            callback=cast(
                Callable[[WSchema.State, WappstoMethod], None],
                self.__callbacks['onCreate'],
            )
        )

    def onRefresh(
        self,
        callback: Callable[['Value'], None],
    ) -> Callable[['Value'], None]:
        """
        Add trigger for when a Refresh where requested.

        A Refresh is typical use to request a update of the report value,
        in case of the natural update cycle is not fast enough for the user,
        or a extra sample are wanted at that given time.

        Callback:
            ValueObj: This object that have had a refresh request for.
        """
        if not self.__argumentCountCheck(callback, 1):
            raise TypeError("The onRefresh callback, is called with 1 argument.")

        def _cb(obj: WSchema.State, method: WappstoMethod) -> None:
            try:
                if method == WappstoMethod.GET:
                    callback(self)
            except Exception:
                self.log.exception("onRefresh callback error.")
                raise

        self.__callbacks['onRefresh'] = _cb

        self.connection.subscribe_state_event(
            uuid=self.children_name_mapping[WSchema.StateType.REPORT],
            callback=_cb
        )

        return callback

    def cancelOnRefresh(self) -> None:
        """Cancel the callback set in onRefresh-method."""
        self.connection.unsubscribe_state_event(
            uuid=self.children_name_mapping[WSchema.StateType.REPORT],
            callback=cast(
                Callable[[WSchema.State, WappstoMethod], None],
                self.__callbacks['onRefresh'],
            )
        )

    def onDelete(
        self,
        callback: Callable[['Value'], None],
    ) -> Callable[['Value'], None]:
        """For when a 'DELETE' request have been called on this element."""
        if not self.__argumentCountCheck(callback, 1):
            raise TypeError("The onDelete callback, is called with 1 argument.")

        def _cb(obj: WSchema.ValueUnion, method: WappstoMethod) -> None:
            try:
                if method == WappstoMethod.DELETE:
                    callback(self)
            except Exception:
                self.log.exception("onDelete callback error.")
                raise

        self.__callbacks['onDelete'] = _cb

        self.connection.subscribe_value_event(
            uuid=self.uuid,
            callback=_cb
        )

        return callback

    def cancelOnDelete(self) -> None:
        """Cancel the callback set in onDelete-method."""
        self.connection.unsubscribe_value_event(
            uuid=self.uuid,
            callback=cast(
                Callable[[WSchema.ValueUnion, WappstoMethod], None],
                self.__callbacks['onDelete'],
            )
        )

    # -------------------------------------------------------------------------
    #   Value methods
    # -------------------------------------------------------------------------

    def refresh(self) -> None:
        """Not implemented."""
        raise NotImplementedError("Method: 'refresh' is not Implemented.")

    def change(self, name: str, value: Any) -> None:
        """
        Update a parameter in the Value structure.

        A parameter that a device can have that can be updated could be:
         - Name
         - Description
         # - Unit
         # - min/max/step/encoding
         - period
         - delta
         # - meaningful_zero
        """
        # raise NotImplementedError("Method: 'change' is not Implemented.")
        pass

    def delete(self) -> None:
        """Request a delete of the Device, & all it's Children."""
        self.connection.delete_value(uuid=self.uuid)

    def _update_local_report(self, data: LogValue) -> None:
        if (
            data.timestamp and self.report_state.timestamp or not self.report_state.timestamp
        ):
            self.report_state = self.report_state.model_copy(update=data.model_dump(exclude_none=True))
            self.report_state.timestamp = data.timestamp
            if self.report_state.timestamp:
                self.report_state.timestamp = self.report_state.timestamp.replace(tzinfo=None)

    def report(
        self,
        value: Union[int, float, str, LogValue, List[LogValue], None],
        timestamp: Optional[datetime] = None
    ) -> None:
        """
        Report the new current value to Wappsto.

        The Report value is typical a measured value from a sensor,
        whether it is a GPIO pin, a analog temperature sensor or a
        device over a I2C bus.

        ERROR: https://github.com/pydantic/pydantic/issues/4852

        """
        # TODO: Check if this value have a state that is read.
        self.log.info(f"Sending Report for: {self.report_state.meta.id}")

        data: LogValue

        if isinstance(value, list):
            if not len(value):
                return

            # TODO: Make sure the timestamps are set.
            sorted_values = sorted(value, key=lambda r: r.timestamp)
            self._update_local_report(sorted_values[-1])

            self.connection.put_bulk_state(
                uuid=self.children_name_mapping[WSchema.StateType.REPORT],
                data=[
                    LogValue(
                        data=x.data,
                        timestamp=x.timestamp
                    ) for x in sorted_values
                ],
            )
            return

        if not isinstance(value, LogValue):
            the_timestamp = timestamp if timestamp is not None else datetime.utcnow()
            data = LogValue(
                data=str(value),
                timestamp=the_timestamp,
            )
        else:
            # TODO: Make sure the timestamp is set.
            data = value

        self._update_local_report(data)

        # NOTE: Single Report
        self.connection.put_state(
            uuid=self.children_name_mapping[WSchema.StateType.REPORT],
            data=data,
        )

    # def report(
    #     self,
    #     value: Union[int, float, str, LogValue, List[LogValue], None],
    #     timestamp: Optional[datetime] = None
    # ) -> None:
    #     """
    #     Report the new current value to Wappsto.

    #     The Report value is typical a measured value from a sensor,
    #     whether it is a GPIO pin, a analog temperature sensor or a
    #     device over a I2C bus.

    #     ERROR: https://github.com/pydantic/pydantic/issues/4852

    #     """
    #     # TODO: Check if this value have a state that is read.
    #     self.log.info(f"Sending Report for: {self.report_state.meta.id}")

    #     the_timestamp = timestamp if timestamp is not None else datetime.utcnow()
    #     data = WSchema.State(
    #         data=value,
    #         timestamp=timestamp_converter(the_timestamp)
    #     )
    #     if (
    #         data.timestamp and self.report_state.timestamp or not self.report_state.timestamp
    #     ):
    #         self.report_state = self.report_state.copy(update=data.model_dump(exclude_none=True))
    #         self.report_state.timestamp = the_timestamp
    #         if self.report_state.timestamp:
    #             self.report_state.timestamp = self.report_state.timestamp.replace(tzinfo=None)
    #     self.connection.put_state(
    #         uuid=self.children_name_mapping[WSchema.StateType.REPORT],
    #         data=data
    #     )

    def control(
        self,
        value: Union[int, float, str, None],
        timestamp: Optional[datetime] = None
    ) -> None:
        """
        Report the a new control value to Wappsto.

        A Control value is typical only changed if a target wanted value,
        have changed, whether it is because of an on device user controller,
        or the target was outside a given range.

        ERROR: https://github.com/pydantic/pydantic/issues/4852

        """
        self.log.info(f"Sending Control for: {self.control_state.meta.id}")
        the_timestamp = timestamp if timestamp is not None else datetime.utcnow()
        data = WSchema.State(
            data=str(value),
            timestamp=the_timestamp,
        )
        if (
            data.timestamp and self.control_state.timestamp or self.control_state.timestamp
        ):
            self.control_state = self.control_state.model_copy(update=data.model_dump(exclude_none=True))
            self.control_state.timestamp = the_timestamp
            if self.control_state.timestamp:
                self.control_state.timestamp = self.control_state.timestamp.replace(tzinfo=None)
        self.connection.put_state(
            uuid=self.children_name_mapping[WSchema.StateType.CONTROL],
            data=data
        )

    # -------------------------------------------------------------------------
    #   Other methods
    # -------------------------------------------------------------------------

    def _createStates(self, permission: PermissionType) -> None:
        if permission in [PermissionType.READ, PermissionType.READWRITE]:
            self._CreateReport()
        if permission in [PermissionType.WRITE, PermissionType.READWRITE]:
            self._CreateControl()

    def _CreateReport(self) -> None:
        if not self.children_name_mapping.get(WSchema.StateType.REPORT):
            self.children_name_mapping[WSchema.StateType.REPORT] = uuid.uuid4()

            self.report_state = WSchema.State(
                data="NA" if self.value_type == ValueBaseType.NUMBER else "",
                type=WSchema.StateType.REPORT,
                meta=WSchema.StateMeta(
                    id=self.children_name_mapping.get(WSchema.StateType.REPORT)
                )
            )

            self.connection.post_state(value_uuid=self.uuid, data=self.report_state)

    def _CreateControl(self) -> None:
        if not self.children_name_mapping.get(WSchema.StateType.CONTROL):
            self.children_name_mapping[WSchema.StateType.CONTROL] = uuid.uuid4()

            self.control_state = WSchema.State(
                data="NA" if self.value_type == ValueBaseType.NUMBER else "",
                type=WSchema.StateType.CONTROL,
                meta=WSchema.StateMeta(
                    id=self.children_name_mapping[WSchema.StateType.CONTROL]
                )
            )
            self.connection.post_state(value_uuid=self.uuid, data=self.control_state)

        def _cb(obj: WSchema.State, method: WappstoMethod) -> None:
            try:
                if method == WappstoMethod.PUT:
                    if (
                        obj.timestamp and self.control_state.timestamp or not self.control_state.timestamp
                    ):
                        self.log.info(f"Control Value updated: {self.uuid}, {obj.data}")
                        self.control_state = self.control_state.model_copy(update=obj.model_dump(exclude_none=True))
                        if self.control_state.timestamp:
                            self.control_state.timestamp = str_to_datetime(self.control_state.timestamp)
                            self.control_state.timestamp = self.control_state.timestamp.replace(tzinfo=None)
            except Exception:
                self.log.exception("onCreateControl callback error.")
                raise

        self.connection.subscribe_state_event(
            uuid=self.children_name_mapping[WSchema.StateType.CONTROL],
            callback=_cb
        )

    def close(self) -> None:
        """Do nothing, only here for compatibility."""
        pass
