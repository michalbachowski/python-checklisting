import io
from abc import abstractmethod
from typing import Generic, TypeVar

import yaml

_R = TypeVar('R')


class BaseParser(Generic[_R]):

    @abstractmethod
    def load(self, stream: io.BufferedIOBase) -> _R:
        pass


class YamlParser(BaseParser[_R]):

    def load(self, stream: io.BufferedIOBase) -> _R:
        return yaml.load(stream)
