import uuid
import datetime

from enum import Enum

from typing import Any
from typing import Callable
from typing import Dict
from typing import Optional
from typing import Union
from pydantic import UUID4

from WappstoIoT.Service.Template import ServiceClass
# from WappstoIoT.Modules.Template import _UnitsInfo
from WappstoIoT.Modules.Template import ValueBaseType
from WappstoIoT.schema import base_schema as WSchema
from WappstoIoT.schema.base_schema import PermissionType
from WappstoIoT.schema.iot_schema import WappstoMethod

from WappstoIoT.utils import Timestamp

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    # NOTE: To avoid ciclic import
    from WappstoIoT.Modules.Device import Device


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
        type: ValueBaseType,
        value_id: int,
        value_uuid: Optional[UUID4] = None,  # Only used on loading.
        name: Optional[str] = None,
        permission: PermissionType = PermissionType.READWRITE,
        min_range: Optional[Union[int, float]] = None,
        max_range: Optional[Union[int, float]] = None,
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

        self.schema = self.__value_type_2_Schema[type]
        self.parent = parent
        self.element: Union[
            WSchema.StringValue,
            WSchema.NumberValue,
            WSchema.BlobValue,
            WSchema.XmlValue
        ]
        self.__id: int = value_id
        self.__uuid: UUID4 = value_uuid if value_uuid else uuid.uuid4()

        self.children_uuid_mapping: Dict[UUID4, Value] = {}
        self.children_id_mapping: Dict[int, UUID4] = {}
        self.children_name_mapping: Dict[str, UUID4] = {}

        self.connection: ServiceClass = parent.connection

        subValue = self.__parseValueType(
                ValueType=type,
                encoding=encoding,
                mapping=mapping,
                max_range=max_range,
                meaningful_zero=meaningful_zero,
                min_range=min_range,
                namespace=namespace,
                ordered_mapping=ordered_mapping,
                si_conversion=si_conversion,
                step=step,
                unit=unit,
                xsd=xsd,
        )

        element = self.connection.get_value(self.uuid)

        if element:
            self.__update_self(element)
        else:
            self.element = self.schema(
                name=name,
                description=description,
                period=period,
                delta=delta,
                permission=permission,
                **subValue,
                meta=WSchema.BaseMeta(
                    id=self.uuid
                )
            )
            self.connection.post_value(
                device_uuid=self.parent.uuid,
                data=self.element
            )

        self._createStates(permission)

        # TODO: create States.

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
        return self.element.name

    @property
    def uuid(self) -> UUID4:
        """Returns the name of the value."""
        return self.__uuid

    @property
    def id(self) -> int:
        return self.__id

    # -------------------------------------------------------------------------
    #   Helper methods
    # -------------------------------------------------------------------------

    def __parseValueType(
        self,
        ValueType,
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

        if ValueType == ValueBaseType.NUMBER:
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
        elif ValueType == ValueBaseType.XML:
            subValue = {
                "xml": WSchema.Xml(
                    xsd=xsd,
                    namespace=namespace,
                )
            }
        elif ValueType == ValueBaseType.STRING:
            subValue = {
                "string": WSchema.String(
                    max=max_range,
                    encoding=encoding
                )
            }
        elif ValueType == ValueBaseType.BLOB:
            subValue = {
                "blob": WSchema.Blob(
                    max=max_range,
                    encoding=encoding
                )
            }

        return subValue

    # def _get_json(self) -> _UnitsInfo:
    #     """Generate the json-object ready for to be saved in the configfile."""
    #     unit_list = []
    #     for unit in self.children_uuid_mapping.values():
    #         unit_list.extend(unit._get_json())
    #     unit_list.append(_UnitsInfo(
    #         self_type=WappstoObjectType.VALUE,
    #         self_id=self.id,
    #         parent=self.parent.uuid,
    #         permission=self.element.permission,
    #         children=list(self.children_uuid_mapping.keys()),
    #         children_id_mapping=self.children_id_mapping,
    #         children_name_mapping=self.children_name_mapping
    #     ))
    #     return unit_list

    def __update_self(self, element):
        # NOTE: If Element Diff from self. Post the local diff.
        pass

    # -------------------------------------------------------------------------
    #   Value 'on-' methods
    # -------------------------------------------------------------------------

    def onChange(
        self,
        callback: Callable[['Value', ChangeType], None],
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
        callback: Callable[['Value', Union[str, int, float]], None],
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
        callback: Callable[['Value', RequestType, str, Any], None],
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
        callback: Callable[['Value', Union[str, int, float]], None],
    ) -> None:
        """
        Add trigger for when a Control request have been make.

        A Control value is typical use to request a new target value,
        for the given value.

        Callback:
            ValueObj: This object that have had a request for.
            any: The Data.
        """

        def _cb(obj, method):
            if method == WappstoMethod.PUT:
                callback(self, obj.data)

        self.connection.subscribe_state_event(
            uuid=self.children_name_mapping[WSchema.StateType.CONTROL.name],
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
            if method == WappstoMethod.GET:
                callback(self, obj.value)

        self.connection.subscribe_state_event(
            uuid=self.children_name_mapping[WSchema.StateType.REPORT.name],
            callback=_cb
        )

    def onDelete(
        self,
        callback: Callable[['Value'], None],
    ) -> None:
        """For when a 'DELETE' request have been called on this element."""
        pass

    # -------------------------------------------------------------------------
    #   Value methods
    # -------------------------------------------------------------------------

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
        """
        Request a delete of the Device, & all it's Children.
        """

        self.connection.delete_value(uuid=self.uuid)
        self._delete()

    def _delete(self):
        # TODO: REDO!
        for c_uuid, c_obj in self.children_uuid_mapping.items():
            c_obj._delete()
            self.children_id_mapping.pop(c_obj.id)
            self.children_name_mapping.pop(c_obj.name)
        self.children_uuid_mapping.clear()

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
        self.connection.put_state(
            uuid=self.children_name_mapping[WSchema.StateType.REPORT.name],
            data=WSchema.State(
                data=value,
                timestamp=timestamp if timestamp else Timestamp.timestamp()
            )
        )

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

    # -------------------------------------------------------------------------
    #   Other methods
    # -------------------------------------------------------------------------

    def _createStates(self, permission: PermissionType):
        if (
            permission == PermissionType.READ or
            permission == PermissionType.READWRITE
        ):
            self._CreateReport(uuid.uuid4())
        if (
            permission == PermissionType.WRITE or
            permission == PermissionType.READWRITE
        ):
            self._CreateControl(uuid.uuid4())

    def _CreateReport(self, state_uuid):
        report_uuid = uuid.uuid4()
        data = WSchema.State(
            data=float("NaN"),
            type=WSchema.StateType.REPORT,
            meta=WSchema.BaseMeta(
                id=report_uuid
            )
        )
        self.children_name_mapping[WSchema.StateType.REPORT.name] = report_uuid

        self.connection.post_state(value_uuid=self.uuid, data=data)

    def _CreateControl(self, state_uuid):
        control_uuid = uuid.uuid4()
        data = WSchema.State(
            data=float("NaN"),
            type=WSchema.StateType.CONTROL,
            meta=WSchema.BaseMeta(
                id=control_uuid
            )
        )
        self.children_name_mapping[WSchema.StateType.CONTROL.name] = control_uuid

        self.connection.post_state(value_uuid=self.uuid, data=data)

    def close(self):
        pass
