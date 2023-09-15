"""Contain the Device Object."""
import uuid
import logging

from enum import Enum

from typing import Any
from typing import Callable
from typing import cast
from typing import Dict
from typing import Optional
from typing import Union

from ..service.template import ServiceClass

from ..schema import base_schema as WSchema
from ..schema.iot_schema import WappstoMethod
from ..schema.base_schema import PermissionType

from .value import Value
from .template import valueSettings
from .template import ValueTemplate
from .template import ValueBaseType

from ..utils import name_check

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    # NOTE: To avoid circle import
    from .network import Network


# #############################################################################
#                                 Device Setup
# #############################################################################

# class RequestType(str, Enum):
#     refresh = "refresh"
#     delete = "delete"


class ChangeType(str, Enum):
    """List of the different value that can be Changed."""
    value = "value"
    name = "name"
    manufacturer = "manufacturer"
    product = "product"
    version = "version"
    serial = "serial"
    description = "description"


class Device:
    """
    A Device is an hardware tool that own different Values.

    By using an example a network of light is structured
    with different light bulbs (devices).
    These devices own their own values of brightness, energy and color.
    """

    schema = WSchema.Device

    def __init__(
        self,
        parent: 'Network',
        device_uuid: Optional[uuid.UUID],
        name: Optional[str] = None,
        manufacturer: Optional[str] = None,
        product: Optional[str] = None,
        version: Optional[str] = None,
        protocol: Optional[str] = None,
        communication: Optional[str] = None,
        serial: Optional[str] = None,
        description: Optional[str] = None,
    ):
        """Configure the Device settings."""
        self.log: logging.Logger = logging.getLogger(__name__)
        self.log.addHandler(logging.NullHandler())

        self.__callbacks: Dict[str, Callable[[WSchema.Device, WappstoMethod], None]] = {}

        self.parent = parent
        self.element: WSchema.Device

        self.children_uuid_mapping: Dict[uuid.UUID, Value] = {}
        self.children_name_mapping: Dict[str, uuid.UUID] = {}

        # self.cloud_id_mapping: Dict[int, uuid.UUID] = {}

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
            protocol=protocol,
            communication=communication,
            meta=WSchema.DeviceMeta(
                version=WSchema.WappstoVersion.V2_0,
                type=WSchema.DeviceMeta.WappstoMetaType.DEVICE,
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
        return cast(str, self.element.name)

    @property
    def uuid(self) -> uuid.UUID:
        """Returns the name of the value."""
        return self.__uuid

    def __update_self(self, element: WSchema.Device) -> None:
        # TODO(MBK): Check if new devices was added! & Check diff.
        # NOTE: If there was a diff, post local one.
        self.element = element.model_copy(update=self.element.model_dump(exclude_none=True))
        self.element.meta = element.meta.model_copy(update=self.element.meta)
        # for nr, value in enumerate(self.element.value):
        #     self.cloud_id_mapping[nr] = value

    def __argumentCountCheck(self, callback: Callable[[Any], Any], requiredArgumentCount: int) -> bool:
        """Check if the required Argument count for given function fits."""
        allArgument: int = callback.__code__.co_argcount
        the_default_count: int = len(callback.__defaults__) if callback.__defaults__ is not None else 1
        mandatoryArguments: int = callback.__code__.co_argcount - the_default_count
        return (
            requiredArgumentCount <= allArgument and requiredArgumentCount >= mandatoryArguments
        )

    # -------------------------------------------------------------------------
    #   Device 'on-' methods
    # -------------------------------------------------------------------------

    def onDelete(
        self,
        callback: Callable[['Device'], None],
    ) -> Callable[['Device'], None]:
        """
        Configure an action when a Delete on this Device have been Requested.

        Normally when a Delete have been requested,
        it is when it is not wanted anymore.
        Which mean that all the device and it's values have to be removed,
        and the process of setting up the device, should be executed again.
        This could result in the same device are created again, or if the
        device was not found, it will just be removed.
        """
        if not self.__argumentCountCheck(callback, 1):
            raise TypeError("The onDelete callback, is called with 1 argument.")

        def _cb(obj: WSchema.Device, method: WappstoMethod) -> None:
            try:
                if method in WappstoMethod.DELETE:
                    callback(self)
            except Exception:
                self.log.exception("onDelete callback error.")
                raise

        self.__callbacks['onDelete'] = _cb

        self.connection.subscribe_device_event(
            uuid=self.uuid,
            callback=_cb
        )

        return callback

    def cancelOnDelete(self) -> None:
        """Cancel the callback set in onDelete-method."""
        self.connection.unsubscribe_device_event(
            uuid=self.uuid,
            callback=self.__callbacks['onDelete']
        )

    def onRefresh(
        self,
        callback: Callable[['Device'], None],
    ) -> Callable[['Device'], None]:
        """
        Add trigger for when a Refresh where requested.

        # It can not! there is no '{"status":"update"}' that can be set.

        Callback:
            ValueObj: This object that have had a refresh request for.
        """
        if not self.__argumentCountCheck(callback, 1):
            raise TypeError("The onRefresh callback, are called with 1 argument.")

        def _cb(obj: WSchema.Device, method: WappstoMethod) -> None:
            try:
                if method in WappstoMethod.GET:
                    callback(self)
            except Exception:
                self.log.exception("onRefresh callback error.")
                raise

        self.__callbacks['onRefresh'] = _cb

        self.connection.subscribe_device_event(
            uuid=self.uuid,
            callback=_cb
        )

        return callback

    def cancelOnRefresh(self) -> None:
        """Cancel the callback set in onRefresh-method."""
        self.connection.unsubscribe_device_event(
            uuid=self.uuid,
            callback=self.__callbacks['onRefresh']
        )

    def onChange(
        self,
        callback: Callable[['Device'], None],
    ) -> Callable[['Device'], None]:
        """Configure a callback for when a change to the Device have occurred."""
        if not self.__argumentCountCheck(callback, 1):
            raise TypeError("The onChange callback, are called with 1 argument.")

        def _cb(obj: WSchema.Device, method: WappstoMethod) -> None:
            try:
                if method in WappstoMethod.PUT:
                    callback(self)
            except Exception:
                self.log.exception("OnChange callback error.")
                raise

        self.__callbacks['onChange'] = _cb

        self.connection.subscribe_device_event(
            uuid=self.uuid,
            callback=_cb
        )

        return callback

    def cancelOnChange(self) -> None:
        """Cancel the callback set in onChange-method."""
        self.connection.unsubscribe_device_event(
            uuid=self.uuid,
            callback=self.__callbacks['onChange']
        )

    def onCreate(
        self,
        callback: Callable[['Device'], None],
    ) -> Callable[['Device'], None]:
        """Configure a callback for when a request have been make for the Value."""
        if not self.__argumentCountCheck(callback, 1):
            raise TypeError("The onCreate callback, are called with 1 argument.")

        def _cb(obj: WSchema.Device, method: WappstoMethod) -> None:
            try:
                if method in WappstoMethod.POST:
                    callback(self)
            except Exception:
                self.log.exception("onCreate callback error.")
                raise

        self.__callbacks['onCreate'] = _cb

        self.connection.subscribe_device_event(
            uuid=self.uuid,
            callback=_cb
        )

        return callback

    def cancelOnCreate(self) -> None:
        """Cancel the callback set in onCreate-method."""
        self.connection.unsubscribe_device_event(
            uuid=self.uuid,
            callback=self.__callbacks['onCreate']
        )

    # -------------------------------------------------------------------------
    #   Device methods
    # -------------------------------------------------------------------------

    def refresh(self) -> None:
        """Not Implemented."""
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
        """Request a delete of the Device, & all it's Children."""
        self.connection.delete_device(uuid=self.uuid)

    # -------------------------------------------------------------------------
    #   Other methods
    # -------------------------------------------------------------------------

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
        """
        Create a Wappsto Number Value.

        A Wappsto Value is where the changing data can be found & are handled.

        This require you to setup manually, that `createValue`
        with `value_template` setup for you.
        """
        kwargs = locals()
        kwargs.pop('self')

        illegal_chars: str = name_check.illegal_characters(name)

        if illegal_chars:
            raise ValueError(
                f"Given name contain a illegal character: {illegal_chars}\n"
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
        *,
        permission: PermissionType,
        type: str,
        max: Union[int, float],
        encoding: Optional[str] = None,
        description: Optional[str] = None,
        period: Optional[int] = None,  # in Sec
        delta: Optional[Union[int, float]] = None,
    ) -> Value:
        """
        Create a Wappsto String Value.

        A Wappsto Value is where the changing data can be found & are handled.

        This require you to setup manually, that `createValue`
        with `value_template` setup for you.
        """
        kwargs = locals()
        kwargs.pop('self')

        illegal_chars: str = name_check.illegal_characters(name)

        if illegal_chars:
            raise ValueError(
                f"Given name contain a illegal character: {illegal_chars}\n"
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
        *,
        permission: PermissionType,
        type: str,
        max: Union[int, float],
        encoding: Optional[str] = None,
        description: Optional[str] = None,
        period: Optional[int] = None,  # in Sec
        delta: Optional[Union[int, float]] = None,
    ) -> Value:
        """
        Create a Wappsto BLOB Value.

        A Wappsto Value is where the changing data can be found & are handled.

        This require you to setup manually, that `createValue`
        with `value_template` setup for you.
        """
        kwargs = locals()
        kwargs.pop('self')

        illegal_chars: str = name_check.illegal_characters(name)

        if illegal_chars:
            raise ValueError(
                f"Given name contain a illegal character: {illegal_chars}\n"
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
        *,
        permission: PermissionType,
        type: str,
        xsd: Optional[str] = None,
        namespace: Optional[str] = None,
        description: Optional[str] = None,
        period: Optional[int] = None,  # in Sec
        delta: Optional[Union[int, float]] = None,
    ) -> Value:
        """
        Create a Wappsto XML Value.

        A Wappsto Value is where the changing data can be found & are handled.

        This require you to setup manually, that `createValue`
        with `value_template` setup for you.
        """
        kwargs = locals()
        kwargs.pop('self')

        illegal_chars: str = name_check.illegal_characters(name)

        if illegal_chars:
            raise ValueError(
                f"Given name contain a illegal character: {illegal_chars}\n"
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
        permission: PermissionType,
        value_template: ValueTemplate,
        description: Optional[str] = None,
    ) -> Value:
        """
        Create a Wappsto Value.

        A Wappsto Value is where the changing data can be found & are handled.

        If a value_template have been set, that means that the parameters like:
        name, permission, min, max, step, encoding & unit have been set
        for you, to be the right settings for the given type. But you can
        still change it, if you choose sow.
        """
        illegal_chars: str = name_check.illegal_characters(name)

        if illegal_chars:
            raise ValueError(
                f"Given name contain a illegal character: {illegal_chars}\n"
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
            **valueSettings[value_template].model_dump()
        )

        self.__add_value(value_obj, name)
        return value_obj

    def __add_value(self, value: Value, name: str) -> None:
        """Helper function for Create, to only localy create it."""
        self.children_uuid_mapping[value.uuid] = value
        self.children_name_mapping[name] = value.uuid

    def close(self) -> None:
        """Do nothing, only here for compatibility."""
        pass
