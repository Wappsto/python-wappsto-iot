from typing import Any
from typing import Callable
from typing import Union
from typing import Optional

from abc import ABC, abstractmethod


class ServiceClass(ABC):

    @abstractmethod
    def post_network(self, uuid, data) -> bool:
        pass

    @abstractmethod
    def put_network(self, uuid, data) -> bool:
        pass

    @abstractmethod
    def get_network(self, uuid, data) -> bool:
        pass

    @abstractmethod
    def delete_network(self, uuid, data) -> bool:
        pass

    @abstractmethod
    def post_device(self, uuid, data) -> bool:
        pass

    @abstractmethod
    def put_device(self, uuid, data) -> bool:
        pass

    @abstractmethod
    def get_device(self, uuid, data) -> bool:
        pass

    @abstractmethod
    def delete_device(self, uuid, data) -> bool:
        pass

    @abstractmethod
    def post_value(self, uuid, data) -> bool:
        pass

    @abstractmethod
    def put_value(self, uuid, data) -> bool:
        pass

    @abstractmethod
    def get_value(self, uuid, data) -> bool:
        pass

    @abstractmethod
    def delete_value(self, uuid, data) -> bool:
        pass

    @abstractmethod
    def post_state(self, uuid, data) -> bool:
        pass

    @abstractmethod
    def put_state(self, uuid, data) -> bool:
        pass

    @abstractmethod
    def get_state(self, uuid, data) -> bool:
        pass

    @abstractmethod
    def delete_state(self, uuid, data) -> bool:
        pass
