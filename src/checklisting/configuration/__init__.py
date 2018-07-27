from abc import ABC, abstractmethod
from typing import Generic, TypeVar

_R = TypeVar('R')


class BaseRawConfiguration(Generic[_R], ABC):

    @abstractmethod
    def raw_config(self) -> _R:
        pass
