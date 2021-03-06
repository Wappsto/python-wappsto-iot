import uuid
import logging

from enum import Enum
from datetime import datetime

from typing import Any
from typing import Callable
from typing import Dict
from typing import Optional
from typing import Union

from ..service.template import ServiceClass
# from .template import dict_diff
from .template import ValueBaseType
# from .template import valueSettings
from ..schema import base_schema as WSchema
from ..schema.base_schema import PermissionType
from ..schema.iot_schema import WappstoMethod

from ..utils import Timestamp

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    # NOTE: To avoid ciclic import
    from .device import Device

# #############################################################################
#                                 Value Setup
# #############################################################################


class Period(str, Enum):
    PERIODIC_REFRESH = "periodic"
    DROP_UNTIL = "drop"


class Delta(str, Enum):
    ONLY_UPDATE_IF = ""
    EXTRA_UPDATES = ""


class Value:

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
        min: Optional[Union[int, float]] = None,
        max: Optional[Union[int, float]] = None,
        step: Optional[Union[int, float]] = None,
        encoding: Optional[str] = None,
        xsd: Optional[str] = None,
        namespace: Optional[str] = None,
        period: Optional[int] = None,  # in Sec
        delta: Optional[Union[int, float]] = None,
        description: Optional[str] = None,
        meaningful_zero: Optional[str] = None,
        mapping: Optional[bool] = None,
        ordered_mapping: Optional[bool] = None,
        si_conversion: Optional[str] = None,
        unit: Optional[str] = None,
    ):
        self.log = logging.getLogger(__name__)
        self.log.addHandler(logging.NullHandler())

        self.value_type = value_type

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

        self.children_name_mapping: Dict[str, uuid.UUID] = {}

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
                type=WSchema.WappstoMetaType.VALUE,
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
        return self.control_state.timestamp

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
        return self.report_state.timestamp

    @property
    def name(self) -> str:
        """Returns the name of the value."""
        return self.element.name

    @property
    def uuid(self) -> uuid.UUID:
        """Returns the uuid of the value."""
        return self.__uuid

    # -------------------------------------------------------------------------
    #   Helper methods
    # -------------------------------------------------------------------------

    def __parseValueTemplate(
        self,
        ValueBaseType,
        encoding,
        mapping,
        max_range,
        meaningful_zero,
        min_range,
        namespace,
        ordered_mapping,
        si_conversion,
        step,
        unit,
        xsd,
    ):

        if ValueBaseType == ValueBaseType.NUMBER:
            subValue = {
                "number": WSchema.Number(
                    min=min_range,
                    max=max_range,
                    step=step,
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

    def __update_self(self, element):
        old_type = type(element)
        new_type = type(self.element)

        new_dict = element.copy(update=self.element.dict(exclude_none=True))
        new_dict.meta = element.meta.copy(update=new_dict.meta)

        if new_type is old_type:
            self.element = new_dict

            if old_type is WSchema.NumberValue:
                new_dict.number = element.number.copy(
                    update=new_dict.number
                )
            elif old_type is WSchema.StringValue:
                new_dict.string = element.string.copy(
                    update=new_dict.string
                )
            elif old_type is WSchema.BlobValue:
                new_dict.blob = element.blob.copy(
                    update=new_dict.blob
                )
            elif old_type is WSchema.XmlValue:
                new_dict.xml = element.xml.copy(
                    update=new_dict.xml
                )
        else:
            new_dict = new_dict.dict(exclude_none=True)
            if old_type is WSchema.StringValue:
                new_dict.pop('string')
            elif old_type is WSchema.NumberValue:
                new_dict.pop('number')
            elif old_type is WSchema.BlobValue:
                new_dict.pop('blob')
            elif old_type is WSchema.XmlValue:
                new_dict.pop('xml')
            self.log.debug(f"CC: {new_dict}")
            self.element = self.schema(**new_dict)

        # TODO: Check for the Difference Value-types & ensure that it is right.

    def __update_state(self):
        state_count = len(self.element.state)
        if self.element.permission == PermissionType.NONE:
            return
        elif state_count == 0:
            self._createStates(self.element.permission)
            return

        state_uuid = self.element.state[0]
        state_obj = self.connection.get_state(uuid=state_uuid)
        self.log.info(f"Found State: {state_uuid} for device: {self.uuid}")
        self.children_name_mapping[state_obj.type.name] = state_uuid

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
        self.children_name_mapping[state_obj.type.name] = state_uuid

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
        def _cb(obj, method):
            try:
                if method in WappstoMethod.PUT:
                    callback(self)
            except Exception:
                self.log.exception("OnChange callback error.")
                raise

        # UNSURE (MBK): on all state & value?
        self.connection.subscribe_value_event(
            uuid=self.uuid,
            callback=_cb
        )

    def onReport(
        self,
        callback: Callable[['Value', Union[str, float]], None],
    ) -> None:
        """
        Add a trigger on when Report data change have been make.

        This trigger even if the Report data was changed to the same value.

        Callback:
            Value: the Object that have had a Report for.
            Union[str, int, float]: The Value of the Report change.
        """
        def _cb_float(obj, method):
            try:
                if method == WappstoMethod.PUT:
                    callback(self, float(obj.data))
            except Exception:
                self.log.exception("onReport callback error.")
                raise

        def _cb_str(obj, method):
            try:
                if method == WappstoMethod.PUT:
                    callback(self, obj.data)
            except Exception:
                self.log.exception("onReport callback error.")
                raise

        _cb = _cb_float if self.value_type == ValueBaseType.NUMBER else _cb_str

        self.connection.subscribe_state_event(
            uuid=self.children_name_mapping[WSchema.StateType.REPORT.name],
            callback=_cb
        )

    def onControl(
        self,
        callback: Callable[['Value', Union[str, float]], None],
    ) -> None:
        """
        Add trigger for when a Control request have been make.

        A Control value is typical use to request a new target value,
        for the given value.

        Callback:
            ValueObj: This object that have had a request for.
            any: The Data.
        """
        def _cb_float(obj, method):
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

        def _cb_str(obj, method):
            try:
                if method == WappstoMethod.PUT:
                    callback(self, obj.data)
            except Exception:
                self.log.exception("onControl callback error.")
                raise

        _cb = _cb_float if self.value_type == ValueBaseType.NUMBER else _cb_str

        self.connection.subscribe_state_event(
            uuid=self.children_name_mapping[WSchema.StateType.CONTROL.name],
            callback=_cb
        )

    def onCreate(
        self,
        callback: Callable[['Value'], None],
    ) -> None:
        """
        Add trigger for when a state was created.

        A Create is typical use to create a new state.

        Callback:
            ValueObj: This object that have had a refresh request for.
        """

        def _cb(obj, method):
            try:
                if method == WappstoMethod.POST:
                    callback(self)
            except Exception:
                self.log.exception("onCreate callback error.")
                raise

        self.connection.subscribe_state_event(
            uuid=self.uuid,
            callback=_cb
        )

    def onRefresh(
        self,
        callback: Callable[['Value'], None],
    ) -> None:
        """
        Add trigger for when a Refresh where requested.

        A Refresh is typical use to request a update of the report value,
        in case of the natural update cycle is not fast enough for the user,
        or a extra sample are wanted at that given time.

        Callback:
            ValueObj: This object that have had a refresh request for.
        """

        def _cb(obj, method):
            try:
                if method == WappstoMethod.GET:
                    callback(self)
            except Exception:
                self.log.exception("onRefresh callback error.")
                raise

        self.connection.subscribe_state_event(
            uuid=self.children_name_mapping[WSchema.StateType.REPORT.name],
            callback=_cb
        )

    def onDelete(
        self,
        callback: Callable[['Value'], None],
    ) -> None:
        """For when a 'DELETE' request have been called on this element."""
        def _cb(obj, method):
            try:
                if method == WappstoMethod.DELETE:
                    callback(self)
            except Exception:
                self.log.exception("onDelete callback error.")
                raise

        self.connection.subscribe_value_event(
            uuid=self.uuid,
            callback=_cb
        )

    # -------------------------------------------------------------------------
    #   Value methods
    # -------------------------------------------------------------------------

    def refresh(self):
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

    def delete(self):
        """
        Request a delete of the Device, & all it's Children.
        """

        self.connection.delete_value(uuid=self.uuid)

    def report(
        self,
        value: Union[int, float, str, None],
        timestamp: Optional[datetime] = None
    ) -> None:
        """
        Report the new current value to Wappsto.

        The Report value is typical a measured value from a sensor,
        whether it is a GPIO pin, a analog temperature sensor or a
        device over a I2C bus.
        """
        # TODO: Check if this value have a state that is read.
        self.log.info(f"Sending Report for: {self.report_state.meta.id}")
        data = WSchema.State(
            data=value,
            timestamp=timestamp if timestamp else Timestamp.timestamp()
        )
        if (
            data.timestamp and self.report_state.timestamp or
            not self.report_state.timestamp
        ):
            self.report_state = self.report_state.copy(update=data.dict(exclude_none=True))
            if self.report_state.timestamp:
                self.report_state.timestamp = self.report_state.timestamp.replace(tzinfo=None)
        self.connection.put_state(
            uuid=self.children_name_mapping[WSchema.StateType.REPORT.name],
            data=data
        )

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
        """
        self.log.info(f"Sending Control for: {self.control_state.meta.id}")

        data = WSchema.State(
            data=value,
            timestamp=timestamp if timestamp else Timestamp.timestamp()
        )
        if (
            data.timestamp and self.control_state.timestamp or
            not self.control_state.timestamp
        ):
            self.control_state = self.control_state.copy(update=data.dict(exclude_none=True))
            if self.control_state.timestamp:
                self.control_state.timestamp = self.control_state.timestamp.replace(tzinfo=None)
        self.connection.put_state(
            uuid=self.children_name_mapping[WSchema.StateType.CONTROL.name],
            data=data
        )

    # -------------------------------------------------------------------------
    #   Other methods
    # -------------------------------------------------------------------------

    def _createStates(self, permission: PermissionType):
        if permission in [PermissionType.READ, PermissionType.READWRITE]:
            self._CreateReport()
        if permission in [PermissionType.WRITE, PermissionType.READWRITE]:
            self._CreateControl()

    def _CreateReport(self):
        if not self.children_name_mapping.get(WSchema.StateType.REPORT.name):
            self.children_name_mapping[WSchema.StateType.REPORT.name] = uuid.uuid4()

            self.report_state = WSchema.State(
                data="NA" if self.value_type == ValueBaseType.NUMBER else "",
                type=WSchema.StateType.REPORT,
                meta=WSchema.BaseMeta(
                    id=self.children_name_mapping.get(WSchema.StateType.REPORT.name)
                )
            )

            self.connection.post_state(value_uuid=self.uuid, data=self.report_state)

    def _CreateControl(self):
        if not self.children_name_mapping.get(WSchema.StateType.CONTROL.name):
            self.children_name_mapping[WSchema.StateType.CONTROL.name] = uuid.uuid4()

            self.control_state = WSchema.State(
                data="NA" if self.value_type == ValueBaseType.NUMBER else "",
                type=WSchema.StateType.CONTROL,
                meta=WSchema.BaseMeta(
                    id=self.children_name_mapping[WSchema.StateType.CONTROL.name]
                )
            )
            self.connection.post_state(value_uuid=self.uuid, data=self.control_state)

        def _cb(obj, method):
            try:
                if method == WappstoMethod.PUT:
                    if (
                        obj.timestamp and self.control_state.timestamp or
                        not self.control_state.timestamp
                    ):
                        self.log.info(f"Control Value updated: {obj.meta.id}, {obj.data}")
                        self.control_state = self.control_state.copy(update=obj.dict(exclude_none=True))
                        if self.control_state.timestamp:
                            self.control_state.timestamp = self.control_state.timestamp.replace(tzinfo=None)
            except Exception:
                self.log.exception("onCreateControl callback error.")
                raise

        self.connection.subscribe_state_event(
            uuid=self.children_name_mapping[WSchema.StateType.CONTROL.name],
            callback=_cb
        )

    def close(self):
        pass
