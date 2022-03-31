import pathlib

from abc import ABC
from abc import abstractmethod

from ..service.template import ServiceClass
from ..utils import observer


class PlugInTemplate(ABC):
    @abstractmethod
    def __init__(
        self,
        config_location: pathlib.Path,
        service: ServiceClass,
        observer: observer  # TODO: Need to be a class. Maybe a Event BUS?
    ):
        pass

    @abstractmethod
    def close(self):
        pass
