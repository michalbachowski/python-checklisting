from abc import ABC, abstractmethod


class BaseRunner(ABC):

    @abstractmethod
    def run(self) -> None:
        pass


class BaseRunnerFactory(ABC):

    @property
    def name(self) -> str:
        return self.__class__.__name__[:-13].lower()

    @abstractmethod
    def provide(self) -> BaseRunner:
        pass
