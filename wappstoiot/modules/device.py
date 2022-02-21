import uuid
import logging

from enum import Enum

from typing import Callable
from typing import Dict
from typing import Optional
from typing import Union

from ..service.template import ServiceClass

from ..schema import base_schema as WSchema
from ..schema.iot_schema import WappstoMethod
from ..schema.base_schema import PermissionType

from .value import Value
from .template import valueSettings
from .template import ValueType
from .template import ValueBaseType

from ..utils import name_check

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    # NOTE: To avoid ciclic import
    from .network import Network


# #############################################################################
#                                 Device Setup
# #############################################################################

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


class Device:

    schema = WSchema.Device

    def __init__(
        self,
        parent: 'Network',
        device_uuid: Optional[uuid.UUID],
        name: Optional[str] = None,
        manufacturer: Optional[str] = None,
        product: Optional[str] = None,
        version: Optional[str] = None,
        serial: Optional[str] = None,
        description: Optional[str] = None,
        # protocol
        # communication
    ):

        self.log = logging.getLogger(__name__)
        self.log.addHandler(logging.NullHandler())

        self.parent = parent
        self.element: WSchema.Device

        self.children_uuid_mapping: Dict[uuid.UUID, Value] = {}
        self.children_name_mapping: Dict[str, uuid.UUID] = {}

        self.cloud_id_mapping: Dict[int, uuid.UUID] = {}

        self.connection: ServiceClass = parent.connection

        element = self.connection.get_device(device_uuid) if device_uuid else None

        self.__uuid: uuid.UUID = device_uuid if device_uuid else uuid.uuid4()

        self.element = self.schema(
            name=name,
            manufacturer=manufacturer,
            product=product,
            version=version,
            serial=serial,
            description=description,
            meta=WSchema.DeviceMeta(
                version=WSchema.WappstoVersion.V2_0,
                type=WSchema.WappstoMetaType.DEVICE,
                id=self.uuid
            )
        )

        if element:
            self.__update_self(element)
            # self.log.debug(
            #     self.element
            # )
            # self.log.debug(
            #     element
            # )
            if self.element != element:
                # TODO: Post diff only.
                self.log.info("Data Models Differ. Sending Local.")
                self.connection.post_device(
                    network_uuid=self.parent.uuid,
                    data=self.element,
                )
        else:
            self.connection.post_device(
                network_uuid=self.parent.uuid,
                data=self.element
            )

    @property
    def name(self) -> str:
        """Returns the name of the value."""
        return self.element.name

    @property
    def uuid(self) -> uuid.UUID:
        """Returns the name of the value."""
        return self.__uuid

    def __update_self(self, element: WSchema.Device):
        # TODO(MBK): Check if new devices was added! & Check diff.
        # NOTE: If there was a diff, post local one.
        self.element = element.copy(update=self.element.dict(exclude_none=True))
        self.element.meta = element.meta.copy(update=self.element.meta)
        for nr, value in enumerate(self.element.value):
            self.cloud_id_mapping[nr] = value

    def _device_name_gen(self, name, value_id):
        return f"{name}_{value_id}"

    # -------------------------------------------------------------------------
    #   Device 'on-' methods
    # -------------------------------------------------------------------------

    def onDelete(
        self,
        callback: Callable[['Device'], None],
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
        def _cb(obj, method):
            try:
                if method in WappstoMethod.DELETE:
                    callback(self)
            except Exception:
                self.log.exception("onDelete callback error.")
                raise

        self.connection.subscribe_device_event(
            uuid=self.uuid,
            callback=_cb
        )

    def onRefresh(
        self,
        callback: Callable[['Device'], None],
    ) -> None:
        """
        Add trigger for when a Refresh where requested.

        # It can not! there is no '{"status":"update"}' that can be set.

        Callback:
            ValueObj: This object that have had a refresh request for.
        """
        def _cb(obj, method):
            try:
                if method in WappstoMethod.GET:
                    callback(self)
            except Exception:
                self.log.exception("onRefresh callback error.")
                raise

        self.connection.subscribe_device_event(
            uuid=self.uuid,
            callback=_cb
        )

    def onChange(
        self,
        callback: Callable[['Device'], None],
    ) -> None:
        """
        Configure a callback for when a change to the Device have occurred.
        """
        def _cb(obj, method):
            try:
                if method in WappstoMethod.PUT:
                    callback(self)
            except Exception:
                self.log.exception("OnChange callback error.")
                raise

        # UNSURE (MBK): on all state & value?
        self.connection.subscribe_device_event(
            uuid=self.uuid,
            callback=_cb
        )

    def onCreate(
        self,
        callback: Callable[['Device'], None],
    ) -> None:
        """
        Configure a callback for when a request have been make for the Value.
        """
        def _cb(obj, method):
            try:
                if method in WappstoMethod.POST:
                    callback(self)
            except Exception:
                self.log.exception("onCreate callback error.")
                raise

        # UNSURE (MBK): on all state & value?
        self.connection.subscribe_device_event(
            uuid=self.uuid,
            callback=_cb
        )

    # -------------------------------------------------------------------------
    #   Device methods
    # -------------------------------------------------------------------------

    def refresh(self):
        raise NotImplementedError("Method: 'refresh' is not Implemented.")

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

    def delete(self) -> None:
        """
        Request a delete of the Device, & all it's Children.
        """
        self.connection.delete_device(uuid=self.uuid)
        self._delete()

    def _delete(self):
        for c_uuid, c_obj in self.children_uuid_mapping.items():
            c_obj._delete()
        self.children_name_mapping.clear()
        self.children_uuid_mapping.clear()

    # -------------------------------------------------------------------------
    #   Other methods
    # -------------------------------------------------------------------------

    def createNumberValue(
        self,
        name: str,
        permission: PermissionType,
        type: str,
        min: Union[int, float],
        max: Union[int, float],
        step: Union[int, float],
        unit: str,
        description: Optional[str],
        si_conversion: Optional[str],
        period: Optional[int] = None,  # in Sec
        delta: Optional[Union[int, float]] = None,
        mapping: Optional[bool] = None,
        meaningful_zero: Optional[bool] = None,
        ordered_mapping: Optional[bool] = None,
    ) -> Value:
        kwargs = locals()
        kwargs.pop('self')

        if not name_check.legal_name(name):
            raise ValueError(
                "Given name contain a ilegal character."
                f"May only contain: {name_check.wappsto_letters}"
            )

        value_uuid = self.connection.get_value_where(
            device_uuid=self.uuid,
            name=name
        )

        value_obj = Value(
            parent=self,
            value_uuid=value_uuid,
            value_type=ValueBaseType.NUMBER,
            **kwargs
        )

        self.__add_value(value_obj, kwargs['name'])
        return value_obj

    def createStringValue(
        self,
        name: str,
        permission: PermissionType,
        type: str,
        max: Union[int, float],
        encoding: Optional[str],
        description: Optional[str],
        period: Optional[int],  # in Sec
        delta: Optional[Union[int, float]],
    ) -> Value:
        kwargs = locals()
        kwargs.pop('self')

        if not name_check.legal_name(name):
            raise ValueError(
                "Given name contain a ilegal character."
                f"May only contain: {name_check.wappsto_letters}"
            )

        value_uuid = self.connection.get_value_where(
            device_uuid=self.uuid,
            name=name
        )

        value_obj = Value(
            parent=self,
            value_uuid=value_uuid,
            value_type=ValueBaseType.STRING,
            **kwargs
        )

        self.__add_value(value_obj, kwargs['name'])
        return value_obj

    def createBlobValue(
        self,
        name: str,
        permission: PermissionType,
        type: str,
        max: Union[int, float],
        encoding: Optional[str],
        description: Optional[str],
        period: Optional[int],  # in Sec
        delta: Optional[Union[int, float]],
    ) -> Value:
        kwargs = locals()
        kwargs.pop('self')

        if not name_check.legal_name(name):
            raise ValueError(
                "Given name contain a ilegal character."
                f"May only contain: {name_check.wappsto_letters}"
            )

        value_uuid = self.connection.get_value_where(
            device_uuid=self.uuid,
            name=name
        )

        value_obj = Value(
            parent=self,
            value_uuid=value_uuid,
            value_type=ValueBaseType.BLOB,
            **kwargs
        )

        self.__add_value(value_obj, kwargs['name'])
        return value_obj

    def createXmlValue(
        self,
        name: str,
        permission: PermissionType,
        type: str,
        xsd: Optional[str],
        namespace: Optional[str],
        description: Optional[str],
        period: Optional[int],  # in Sec
        delta: Optional[Union[int, float]],
    ) -> Value:
        kwargs = locals()
        kwargs.pop('self')

        if not name_check.legal_name(name):
            raise ValueError(
                "Given name contain a ilegal character."
                f"May only contain: {name_check.wappsto_letters}"
            )

        value_uuid = self.connection.get_value_where(
            device_uuid=self.uuid,
            name=name
        )

        value_obj = Value(
            parent=self,
            value_uuid=value_uuid,
            value_type=ValueBaseType.XML,
            **kwargs
        )

        self.__add_value(value_obj, kwargs['name'])
        return value_obj

    def createValue(
        self,
        name: str,
        value_type: ValueType,
        description: Optional[str] = None,
        permission: PermissionType = PermissionType.READWRITE,
    ) -> Value:
        """
        Create a Wappsto Value.

        A Wappsto Value is where the changing data can be found & are handled.

        If a value_type have been set, that means that the parameters like:
        name, permission, min, max, step, encoding & unit have been set
        for you, to be the right settings for the given type. But you can
        still change it, if you choose sow.
        """

        if not name_check.legal_name(name):
            raise ValueError(
                "Given name contain a ilegal character."
                f"May only contain: {name_check.wappsto_letters}"
            )

        value_uuid = self.connection.get_value_where(
            device_uuid=self.uuid,
            name=name
        )

        value_obj = Value(
            parent=self,
            name=name,
            value_uuid=value_uuid,
            permission=permission,
            **valueSettings[value_type].dict()
        )

        self.__add_value(value_obj, name)
        return value_obj

    def __add_value(self, value: Value, name: str):
        """Helper function for Create, to only localy create it."""
        self.children_uuid_mapping[value.uuid] = value
        self.children_name_mapping[name] = value.uuid

    def close(self):
        pass
