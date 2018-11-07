from abc import ABC, abstractmethod
from typing import Generic, TypeVar

R = TypeVar('R')


class BaseRawConfiguration(Generic[R], ABC):

    @abstractmethod
    def raw_config(self) -> R:
        pass
