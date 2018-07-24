from abc import ABC, abstractmethod
from typing import Callable, Iterable, Iterator

from checklisting.task import Checklist


class BaseChecklistsProvider(ABC):

    @abstractmethod
    def get_all(self) -> Iterator[Checklist]:
        pass

    @abstractmethod
    def get_filtered(self, predicate: Callable[[Checklist], bool]) -> Iterator[Checklist]:
        pass


class StaticChecklistsProvider(BaseChecklistsProvider):

    def __init__(self, checklists: Iterable[Checklist]) -> None:
        self._checklists = list(checklists)

    def get_all(self) -> Iterator[Checklist]:
        return iter(self._checklists)

    def get_filtered(self, predicate: Callable[[Checklist], bool]) -> Iterator[Checklist]:
        return filter(predicate, self._checklists)
