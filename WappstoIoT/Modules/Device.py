import uuid

from enum import Enum

from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Union
from pydantic import UUID4

from WappstoIoT.Service.Template import ServiceClass

from WappstoIoT.schema.base_schema import Device as DeviceSchema
from WappstoIoT.schema.base_schema import BaseMeta
# from WappstoIoT.schema.iot_schema import WappstoObjectType
from WappstoIoT.schema.base_schema import PermissionType

from WappstoIoT.Modules.Value import Value
from WappstoIoT.Modules.Template import valueSettings
from WappstoIoT.Modules.Template import ValueType
# from WappstoIoT.Modules.Template import _UnitsInfo

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    # NOTE: To avoid ciclic import
    from WappstoIoT.Modules.Network import Network


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

    schema = DeviceSchema

    def __init__(
        self,
        parent: 'Network',
        device_id: int,
        device_uuid: Optional[UUID4] = None,  # Only used on loading.
        name: Optional[str] = None,
        manufacturer: Optional[str] = None,
        product: Optional[str] = None,
        version: Optional[str] = None,
        serial: Optional[str] = None,
        description: Optional[str] = None,
        # protocol
        # communication
    ):

        self.parent = parent
        self.element: DeviceSchema
        self.__id: int = device_id
        self.__uuid: UUID4 = device_uuid if device_uuid else uuid.uuid4()

        self.children_uuid_mapping: Dict[UUID4, Value] = {}
        self.children_id_mapping: Dict[int, UUID4] = {}
        self.children_name_mapping: Dict[str, UUID4] = {}

        self.connection: ServiceClass = parent.connection

        self.element = self.schema(
            name=name,
            manufacturer=manufacturer,
            product=product,
            version=version,
            serial=serial,
            description=description,
            meta=BaseMeta(
                id=self.uuid
            )
        )

        element = self.connection.get_device(self.uuid)

        if element:
            self.__update_self(element)
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
    def uuid(self) -> UUID4:
        """Returns the name of the value."""
        return self.__uuid

    @property
    def id(self) -> int:
        return self.__id

    # -------------------------------------------------------------------------
    #   Helper methods
    # -------------------------------------------------------------------------

    # def _get_json(self) -> _UnitsInfo:
    #     """Generate the json-object ready for to be saved in the configfile."""
    #     unit_list = []
    #     for unit in self.children_uuid_mapping.values():
    #         unit_list.extend(unit._get_json())
    #     unit_list.append(_UnitsInfo(
    #         self_type=WappstoObjectType.DEVICE,
    #         self_id=self.id,
    #         parent=self.parent.uuid,
    #         children=list(self.children_uuid_mapping.keys()),
    #         children_id_mapping=self.children_id_mapping,
    #         children_name_mapping=self.children_name_mapping
    #     ))
    #     return unit_list

    def __update_self(self, element):
        # NOTE: If Element Diff from self. Post the local diff.
        pass

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
        pass

    def onRefresh(  # TODO: Change me!
        self,
        callback: Callable[['Device'], None],
    ) -> None:
        """
        Add trigger for when a Refresh where requested.

        # It can not! there is no '{"status":"update"}' that can be set.

        Callback:
            ValueObj: This object that have had a refresh request for.
        """
        pass

    def onChange(
        self,
        callback: Callable[['Device', str, Any], None],
        change_type: Optional[Union[List[ChangeType], ChangeType]] = None
    ) -> None:
        """
        Configure a callback for when a change to the Device have occurred.
        """
        pass

    def onRequest(
        self,
        callback: Callable[['Device', str, Any], None],
        request_type: Optional[RequestType] = None
    ) -> None:
        """
        Configure a callback for when a request have been make for the Device.
        """
        pass

    # -------------------------------------------------------------------------
    #   Device methods
    # -------------------------------------------------------------------------

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

    def refresh(self):
        raise NotImplementedError("Method: 'refresh' is not Implemented.")

    def request(self):
        raise NotImplementedError("Method: 'request' is not Implemented.")

    def delete(self):
        """
        Request a delete of the Device, & all it's Children.
        """
        self.connection.delete_device(uuid=self.uuid)
        self._delete()

    def _delete(self):
        for c_uuid, c_obj in self.children_uuid_mapping.items():
            c_obj._delete()
            self.children_id_mapping.pop(c_obj.id)
            self.children_name_mapping.pop(c_obj.name)
        self.children_uuid_mapping.clear()

    # -------------------------------------------------------------------------
    #   Other methods
    # -------------------------------------------------------------------------

    def createValue(
        self,
        name: Optional[str] = None,
        value_id: Optional[int] = None,
        value_type: ValueType = ValueType.DEFAULT,
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
    ) -> Value:
        """
        Create a Wappsto Value.

        A Wappsto Value is where the changing data can be found & are handled.

        If a value_type have been set, that means that the parameters like:
        name, permission, min, max, step, encoding & unit have been set
        for you, to be the right settings for the given type. But you can
        still change it, if you choose sow.
        """
        kwargs = locals()
        kwargs.pop('self')
        kwargs.pop("value_type")

        thisSetting = valueSettings[value_type]

        if not value_id:
            if self.children_id_mapping:
                value_id = max(self.children_id_mapping.keys()) + 1
            else:
                value_id = 0
        # Should we use create re-get a value?
        elif value_id in self.children_id_mapping:
            return self.children_uuid_mapping[self.children_id_mapping[value_id]]

        # the kwargs weigh higher then the default settings. 
        for key, value in thisSetting.dict().items():
            if key in kwargs and kwargs[key] is None:
                kwargs[key] = value

        # kwargs['value_uuid'] = self.parent._configs.units[self.uuid].children_id_mapping.get(value_id)
        # if kwargs['value_uuid']:
        #     kwargs['name'] = self.parent._configs.units[self.uuid].children_name_mapping.get(kwargs['value_uuid'])

        if kwargs['name'] in self.children_name_mapping:
            # If Default value name is in use, gen new!
            kwargs['name'] = self._device_name_gen(thisSetting.name, value_id)

        value_obj = Value(
            parent=self,
            type=thisSetting.type,
            **kwargs
        )

        self.__add_value(value_obj, value_id, kwargs['name'])
        return value_obj

    def __add_value(self, value: Value, id: int, name: str):
        """Helper function for Create, to only localy create it."""
        self.children_uuid_mapping[value.uuid] = value
        self.children_id_mapping[id] = value.uuid
        self.children_name_mapping[name] = value.uuid

    def close(self):
        pass
