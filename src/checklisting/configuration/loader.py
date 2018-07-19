import io
import sys
from abc import ABC, abstractmethod
from pathlib import PurePath


class BaseConfigurationLoader(ABC):

    @abstractmethod
    def load_configuration(self) -> io.BufferedIOBase:
        pass


class FileConfigurationLoader(BaseConfigurationLoader):

    def __init__(self, path: PurePath) -> None:
        super().__init__()
        self._path = path

    def load_configuration(self) -> io.BufferedIOBase:
        with open(self._path, 'r') as stream:
            return io.StringIO("\n".join(stream.readlines()))


class StdinConfigurationLoader(BaseConfigurationLoader):

    def load_configuration(self) -> io.BufferedIOBase:
        return sys.stdin
