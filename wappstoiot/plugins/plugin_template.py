import pathlib

from abc import ABC
from abc import abstractmethod

from ..connections import protocol as ConnectionTemplate
from ..service import template as ServiceTemplate
from ..modules import template as ModuleTemplate

from ..utils import observer


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
