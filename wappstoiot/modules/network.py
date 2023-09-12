"""Contain the Network Object."""
import logging
import uuid

from typing import Any
from typing import Dict
from typing import Callable
from typing import Optional

from ..service.template import ServiceClass
# from .service.rest_api import RestAPI

from .device import Device

from ..schema import base_schema as WSchema
from ..schema.iot_schema import WappstoMethod

from ..utils import name_check


# #############################################################################
#                                 Network Setup
# #############################################################################

class Network(object):
    """
    The root structure/grouping for the IoT Device.

    A network administrates the relationship between different devices.
    For example a network of lights.
    """

    schema = WSchema.Network

    def __init__(
        self,
        name: str,
        connection: ServiceClass,
        network_uuid: uuid.UUID,
        description: str = "",
    ) -> None:
        """Configure the Network settings."""
        self.log = logging.getLogger(__name__)
        self.log.addHandler(logging.NullHandler())

        kwargs = locals()
        self.__uuid: uuid.UUID = network_uuid
        self.element: WSchema.Network

        self.__callbacks: Dict[
            str,
            Callable[[WSchema.Network, WappstoMethod], None],
        ] = {}

        self.children_uuid_mapping: Dict[uuid.UUID, Device] = {}
        self.children_name_mapping: Dict[str, uuid.UUID] = {}

        # self.cloud_id_mapping: Dict[int, uuid.UUID] = {}

        self.connection: ServiceClass = connection

        self.element = self.schema(
            name=name,
            description=description,
            meta=WSchema.NetworkMeta(
                version=WSchema.WappstoVersion.V2_0,
                type=WSchema.NetworkMeta.WappstoMetaType.NETWORK,
                id=self.uuid
            )
        )

        element = self.connection.get_network(self.uuid)
        if element:
            self.__update_self(element)
            # self.log.debug(
            #     type(self.element.meta)
            # )
            # self.log.debug(
            #     self.element.meta
            # )
            # self.log.debug(
            #     type(element.meta)
            # )
            # self.log.debug(
            #     element.meta
            # )
            if self.element != element:
                # TODO: Post diff only.
                self.log.info("Data Models Differ. Sending Local.")
                self.connection.post_network(self.element)
        else:
            self.connection.post_network(self.element)

    @property
    def name(self) -> Optional[str]:
        """Returns the name of the value."""
        return self.element.name

    @property
    def uuid(self) -> uuid.UUID:
        """Returns the name of the value."""
        return self.__uuid

    def __argumentCountCheck(self, callback: Callable[[Any], Any], requiredArgumentCount: int) -> bool:
        """Check if the required Argument count for given function fits."""
        allArgument: int = callback.__code__.co_argcount
        the_default_count: int = len(callback.__defaults__) if callback.__defaults__ is not None else 1
        mandatoryArguments: int = callback.__code__.co_argcount - the_default_count
        return (
            requiredArgumentCount <= allArgument and requiredArgumentCount >= mandatoryArguments
        )

    # -------------------------------------------------------------------------
    #   Save/Load helper methods
    # -------------------------------------------------------------------------

    def __update_self(self, element: WSchema.Network) -> None:
        # TODO(MBK): Check if new devices was added! & Check diff.
        # NOTE: If there was a diff, post local one.
        self.element = element.model_copy(update=self.element.model_dump(exclude_none=True))
        self.element.meta = element.meta.model_copy(update=self.element.meta)
        # for nr, device in enumerate(self.element.device):
        #     self.cloud_id_mapping[nr] = device

    # -------------------------------------------------------------------------
    #   Network 'on-' methods
    # -------------------------------------------------------------------------

    def onChange(
        self,
        callback: Callable[['Network'], None],
    ) -> Callable[['Network'], None]:
        """
        Configure a callback for when a change to the Network have occurred.

        # UNSURE(MBK): How should it get the data back?
        """
        if not self.__argumentCountCheck(callback, 1):
            raise TypeError("The onChange callback, is called with 1 argument.")

        def _cb(obj: WSchema.Network, method: WappstoMethod) -> None:
            try:
                if method == WappstoMethod.PUT:
                    callback(self)
            except Exception:
                self.log.exception("OnChange callback error.")
                raise

        self.__callbacks['onChange'] = _cb

        self.connection.subscribe_network_event(
            uuid=self.uuid,
            callback=_cb
        )

        return callback

    def cancelOnChange(self) -> None:
        """Cancel the callback set in onChange-method."""
        self.connection.unsubscribe_network_event(
            uuid=self.uuid,
            callback=self.__callbacks['onChange']
        )

    def onCreate(
        self,
        callback: Callable[['Network'], None],
    ) -> Callable[['Network'], None]:
        """Configure a callback for when a create have been make for the Device."""
        if not self.__argumentCountCheck(callback, 1):
            raise TypeError("The onCreate callback, is called with 1 argument.")

        def _cb(obj: WSchema.Network, method: WappstoMethod) -> None:
            try:
                if method == WappstoMethod.POST:
                    callback(self)
            except Exception:
                self.log.exception("onCreate callback error.")
                raise

        self.__callbacks['onCreate'] = _cb

        self.connection.subscribe_network_event(
            uuid=self.uuid,
            callback=_cb
        )

        return callback

    def cancelOnCreate(self) -> None:
        """Cancel the callback set in onCreate-method."""
        self.connection.unsubscribe_network_event(
            uuid=self.uuid,
            callback=self.__callbacks['onCreate']
        )

    def onRefresh(
        self,
        callback: Callable[['Network'], None],
    ) -> Callable[['Network'], None]:
        """
        Configure an action when a refresh Network have been Requested.

        Normally when a refresh have been requested on a Network, ...
        ...
        # It can not! there is no '{"status":"update"}' that can be set.
        """
        if not self.__argumentCountCheck(callback, 1):
            raise TypeError("The onRefresh callback, is called with 1 argument.")

        def _cb(obj: WSchema.Network, method: WappstoMethod) -> None:
            try:
                if method == WappstoMethod.GET:
                    callback(self)
            except Exception:
                self.log.exception("onRefresh callback error.")
                raise

        self.__callbacks['onRefresh'] = _cb

        self.connection.subscribe_network_event(
            uuid=self.uuid,
            callback=_cb
        )

        return callback

    def cancelOnRefresh(self) -> None:
        """Cancel the callback set in onRefresh-method."""
        self.connection.unsubscribe_network_event(
            uuid=self.uuid,
            callback=self.__callbacks['onRefresh']
        )

    def onDelete(
        self,
        callback: Callable[['Network'], None],
    ) -> Callable[['Network'], None]:
        """
        Configure an action when a Delete Network have been Requested.

        Normally when a Delete have been requested on a Network,
        it is when it is not wanted anymore, and the Network have been
        unclaimed. Which mean that all the devices & value have to be
        recreated, and/or the program have to close.
        """
        if not self.__argumentCountCheck(callback, 1):
            raise TypeError("The onDelete callback, is called with 1 argument.")

        def _cb(obj: WSchema.Network, method: WappstoMethod) -> None:
            try:
                if method == WappstoMethod.DELETE:
                    callback(self)
            except Exception:
                self.log.exception("onDelete callback error.")
                raise

        self.__callbacks['onDelete'] = _cb

        self.connection.subscribe_network_event(
            uuid=self.uuid,
            callback=_cb
        )

        return callback

    def cancelOnDelete(self) -> None:
        """Cancel the callback set in onDelete-method."""
        self.connection.unsubscribe_network_event(
            uuid=self.uuid,
            callback=self.__callbacks['onDelete']
        )

    # -------------------------------------------------------------------------
    #   Network methods
    # -------------------------------------------------------------------------

    def refresh(self) -> None:
        """Not implemented."""
        raise NotImplementedError("Method: 'refresh' is not Implemented.")

    def change(self) -> None:
        """Not implemented."""
        pass

    def delete(self) -> None:
        """
        Normally it is used to unclaim a Network & delete all children.

        If a network delete itself, it will prompt a factory reset.
        This means that manufacturer and owner will be reset (or not),
        in relation of the rules set up in the certificates.
        """
        self.connection.delete_network(uuid=self.uuid)

    # -------------------------------------------------------------------------
    #   Create methods
    # -------------------------------------------------------------------------

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
    ) -> Device:
        """
        Create a new Wappsto Device.

        A Wappsto Device is references something that is attached to the network
        that can be controlled or have values that can be reported to Wappsto.

        This could be a button that is connected to this unit,
        or in the case of this unit is a gateway, it could be a remote unit.
        """
        kwargs = locals()
        kwargs.pop('self')

        illegal_chars: str = name_check.illegal_characters(name)

        if illegal_chars:
            raise ValueError(
                f"Given name contain a illegal character: {illegal_chars}\n"
                f"May only contain: {name_check.wappsto_letters}"
            )

        device_uuid = self.connection.get_device_where(
            network_uuid=self.uuid,
            name=name
        )

        device_obj = Device(
            parent=self,
            device_uuid=device_uuid,
            **kwargs
        )
        self.__add_device(device_obj, kwargs['name'])
        return device_obj

    def __add_device(self, device: Device, name: str) -> None:
        """Helper function for Create, to only localy create it."""
        self.children_uuid_mapping[device.uuid] = device
        self.children_name_mapping[name] = device.uuid

    def close(self) -> None:
        """Do nothing, only here for compatibility."""
        pass
