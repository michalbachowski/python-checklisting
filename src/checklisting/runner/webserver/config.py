from abc import ABC, abstractproperty


class BaseWebRunnerConfiguration(ABC):

    @abstractproperty
    def webserver_port(self) -> int:
        pass

    @abstractproperty
    def webserver_addr(self) -> str:
        pass
