"""Contain the Service class that handle the data conversion."""
from uuid import UUID
from enum import Enum

from typing import Callable
from typing import List
from typing import Optional
from typing import Union

from abc import ABC
from abc import abstractmethod

from ..schema.base_schema import BlobValue
from ..schema.base_schema import Device
from ..schema.base_schema import LogValue
from ..schema.base_schema import Network
from ..schema.base_schema import NumberValue
from ..schema.base_schema import State
from ..schema.base_schema import StringValue
from ..schema.base_schema import XmlValue
from ..schema.iot_schema import WappstoMethod


class StatusID(str, Enum):
    """The different states the service class can be in."""
    IDLE = "idle"
    # BATCHING = "batching"
    SENDING = "sending"
    SENDERROR = "send Error"
    SEND = "send"
    ERROR = "Error Reply"


class ServiceClass(ABC):
    """Should handle the conversion of the data from the socket and UI."""

    def close(self) -> None:
        """Closes the Service class down."""
        pass
    # #########################################################################
    #                               Helper API
    # #########################################################################

    def _resend_data(self, data: Union[str, bytes]) -> None:
        """For internal resending of data."""
        pass

    def ping(self) -> None:
        """Should send a ping to check the connection."""
        pass

    # #########################################################################
    #                               Network API
    # #########################################################################

    @abstractmethod
    def subscribe_network_event(
        self,
        uuid: UUID,
        callback: Callable[[Network, WappstoMethod], None]
    ) -> None:
        """Subscribe a function to be call on Network changes."""
        pass

    @abstractmethod
    def unsubscribe_network_event(
        self,
        uuid: UUID,
        callback: Callable[[Network, WappstoMethod], None]
    ) -> None:
        """Unsubscribe a function from Network changes."""
        pass

    @abstractmethod
    def post_network(self, data: Network) -> bool:
        """Create the network."""
        pass

    @abstractmethod
    def put_network(self, uuid: UUID, data: Network) -> bool:
        """Make changes to a network."""
        pass

    @abstractmethod
    def get_network(self, uuid: UUID) -> Union[Network, None]:
        """Request the network data."""
        pass

    @abstractmethod
    def delete_network(self, uuid: UUID) -> bool:
        """Remove the network."""
        pass

    # #########################################################################
    #                                Device API
    # #########################################################################

    @abstractmethod
    def subscribe_device_event(
        self,
        uuid: UUID,
        callback: Callable[[Device, WappstoMethod], None]
    ) -> None:
        """Subscribe a function to be call on given Device changes."""
        pass

    @abstractmethod
    def unsubscribe_device_event(
        self,
        uuid: UUID,
        callback: Callable[[Device, WappstoMethod], None]
    ) -> None:
        """Unsubscribe a function from given Device changes."""
        pass

    @abstractmethod
    def post_device(self, network_uuid: UUID, data: Device) -> bool:
        # url=f"/services/2.0/{uuid}/device",
        """Create given device."""
        pass

    @abstractmethod
    def put_device(self, uuid: UUID, data: Device) -> bool:
        """Make changes to a device."""
        pass

    @abstractmethod
    def get_device_where(self, network_uuid: UUID, **kwargs: str) -> Optional[UUID]:
        """Request data from a device with given values."""
        pass

    @abstractmethod
    def get_device(self, uuid: UUID) -> Union[Device, None]:
        """Request to get given device data."""
        pass

    @abstractmethod
    def delete_device(self, uuid: UUID) -> bool:
        """Remove to given device."""
        pass

    # #########################################################################
    #                                 Value API
    # #########################################################################

    ValueUnion = Union[StringValue, NumberValue, BlobValue, XmlValue]

    @abstractmethod
    def subscribe_value_event(
        self,
        uuid: UUID,
        callback: Callable[[ValueUnion, WappstoMethod], None]
    ) -> None:
        """Subscribe a function to be call on given value changes."""
        pass

    @abstractmethod
    def unsubscribe_value_event(
        self,
        uuid: UUID,
        callback: Callable[[ValueUnion, WappstoMethod], None]
    ) -> None:
        """Unsubscribe a function from given value changes."""
        pass

    @abstractmethod
    def post_value(self, device_uuid: UUID, data: ValueUnion) -> bool:
        """Create given value."""
        # url=f"/services/2.0/{uuid}/value",
        pass

    @abstractmethod
    def put_value(self, uuid: UUID, data: ValueUnion) -> bool:
        """Make changes to a value."""
        pass

    @abstractmethod
    def get_value_where(self, device_uuid: UUID, **kwargs: str) -> Optional[UUID]:
        """Request data from a value with given values."""
        pass

    @abstractmethod
    def get_value(self, uuid: UUID) -> Union[ValueUnion, None]:
        """Request to get given value data."""
        pass

    @abstractmethod
    def delete_value(self, uuid: UUID) -> bool:
        """Remove to given value."""
        pass

    # #########################################################################
    #                                State API
    # #########################################################################

    @abstractmethod
    def subscribe_state_event(
        self,
        uuid: UUID,
        callback: Callable[[State, WappstoMethod], None]
    ) -> None:
        """Subscribe a function to be call on given state changes."""
        pass

    @abstractmethod
    def unsubscribe_state_event(
        self,
        uuid: UUID,
        callback: Callable[[State, WappstoMethod], None]
    ) -> None:
        """Unsubscribe a function from given state changes."""
        pass

    @abstractmethod
    def post_state(self, value_uuid: UUID, data: Union[State, LogValue]) -> bool:
        """Create given state."""
        # url=f"/services/2.0/{uuid}/state",
        pass

    @abstractmethod
    def put_bulk_state(self, uuid: UUID, data: List[LogValue]) -> bool:
        """Make bulk changes the given state."""
        pass

    @abstractmethod
    def put_state(self, uuid: UUID, data: Union[State, LogValue]) -> bool:
        """Make changes to a state."""
        pass

    @abstractmethod
    def get_state(self, uuid: UUID) -> Union[State, None]:
        """Request to get given state data."""
        pass

    @abstractmethod
    def delete_state(self, uuid: UUID) -> bool:
        """Remove to given state."""
        pass
