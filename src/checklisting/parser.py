import io
from abc import abstractmethod
from typing import Generic, TypeVar

import yaml

R = TypeVar('R')


class BaseParser(Generic[R]):

    @abstractmethod
    def load(self, stream: io.BufferedIOBase) -> R:
        pass


class YamlParser(BaseParser[R]):

    def load(self, stream: io.BufferedIOBase) -> R:
        return yaml.load(stream)
