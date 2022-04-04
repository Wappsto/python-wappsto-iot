import pathlib

from abc import ABC
from abc import abstractmethod

from ..connections import protocol as ConnectionTemplate   # noqa: F401
from ..service import template as ServiceTemplate   # noqa: F401
from ..modules import template as ModuleTemplate   # noqa: F401

from ..utils import observer   # noqa: F401


class PlugInTemplate(ABC):
    @abstractmethod
    def __init__(
        self,
        config_location: pathlib.Path,
        service: ServiceTemplate.ServiceClass,
        observer: observer,  # TODO: Need to be a class. Maybe a Event BUS?
        **kwargs
    ):
        pass

    @abstractmethod
    def close(self):
        pass
