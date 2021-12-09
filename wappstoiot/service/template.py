from uuid import UUID
from enum import Enum

from typing import Callable
from typing import Dict
from typing import List
from typing import Union

from abc import ABC
from abc import abstractmethod

from ..schema.base_schema import BlobValue
from ..schema.base_schema import Device
from ..schema.base_schema import Network
from ..schema.base_schema import NumberValue
from ..schema.base_schema import State
from ..schema.base_schema import StringValue
from ..schema.base_schema import XmlValue
from ..schema.base_schema import WappstoMethods


class Status(str, Enum):
    IDLE = "idle"
    # BATCHING = "batching"
    SENDING = "sending"
    SENDERROR = "send Error"
    SEND = "send"


class ServiceClass(ABC):

    # #########################################################################
    #                               Network API
    # #########################################################################

    @abstractmethod
    def subscribe_network_event(
        self,
        uuid: UUID,
        callback: Callable[[Network, WappstoMethods], None]
    ):
        pass

    @abstractmethod
    def post_network(self, data) -> bool:
        # url=f"/services/2.0/network/{uuid}",
        pass

    @abstractmethod
    def put_network(self, uuid: UUID, data) -> bool:
        pass

    @abstractmethod
    def get_network(self, uuid: UUID) -> Union[Network, None]:
        pass

    @abstractmethod
    def delete_network(self, uuid: UUID) -> bool:
        pass

    # #########################################################################
    #                                Device API
    # #########################################################################

    @abstractmethod
    def subscribe_device_event(
        self,
        uuid: UUID,
        callback: Callable[[Device, WappstoMethods], None]
    ):
        pass

    @abstractmethod
    def post_device(self, network_uuid: UUID, data: Device) -> bool:
        # url=f"/services/2.0/{uuid}/device",
        pass

    @abstractmethod
    def put_device(self, uuid: UUID, data: Device) -> bool:
        pass

    @abstractmethod
    def get_device_where(self, network_uuid: UUID, **kwargs: Dict[str, str]) -> List[UUID]:
        pass

    @abstractmethod
    def get_device(self, uuid: UUID) -> Union[Device, None]:
        pass

    @abstractmethod
    def delete_device(self, uuid: UUID) -> bool:
        pass

    # #########################################################################
    #                                 Value API
    # #########################################################################

    ValueUnion = Union[StringValue, NumberValue, BlobValue, XmlValue]

    @abstractmethod
    def subscribe_value_event(
        self,
        uuid: UUID,
        callback: Callable[[ValueUnion, WappstoMethods], None]
    ):
        pass

    @abstractmethod
    def post_value(self, device_uuid: UUID, data: ValueUnion) -> bool:
        # url=f"/services/2.0/{uuid}/value",
        pass

    @abstractmethod
    def put_value(self, uuid: UUID, data: ValueUnion) -> bool:
        pass

    @abstractmethod
    def get_value_where(self, device_uuid: UUID, **kwargs: Dict[str, str]) -> List[UUID]:
        pass

    @abstractmethod
    def get_value(self, uuid: UUID) -> Union[ValueUnion, None]:
        pass

    @abstractmethod
    def delete_value(self, uuid: UUID) -> bool:
        pass

    # #########################################################################
    #                                State API
    # #########################################################################

    @abstractmethod
    def subscribe_state_event(
        self,
        uuid: UUID,
        callback: Callable[[State, WappstoMethods], None]
    ):
        pass

    @abstractmethod
    def post_state(self, value_uuid: UUID, data: State) -> bool:
        # url=f"/services/2.0/{uuid}/state",
        pass

    @abstractmethod
    def put_state(self, uuid: UUID, data: State) -> bool:
        pass

    @abstractmethod
    def get_state(self, uuid: UUID) -> Union[State, None]:
        pass

    @abstractmethod
    def delete_state(self, uuid: UUID) -> bool:
        pass
