from abc import abstractmethod
from typing import Iterable, Iterator, Callable
from checklisting.task import Checklist


class BaseChecklistsProvider(Iterable[Checklist]):

    @abstractmethod
    def __iter__(self) -> Iterator[Checklist]:
        pass

    @abstractmethod
    def get_all(self) -> Iterator[Checklist]:
        pass

    @abstractmethod
    def get_filtered(self, predicate: Callable[[Checklist], bool]) -> Iterator[Checklist]:
        pass


class StaticChecklistsProvider(BaseChecklistsProvider):

    def __init__(self, checklists: Iterable[Checklist]) -> None:
        self._checklists = list(checklists)

    def __iter__(self) -> Iterator[Checklist]:
        return iter(self._checklists)

    def get_all(self) -> Iterator[Checklist]:
        return iter(self)

    def get_filtered(self, predicate: Callable[[Checklist], bool]) -> Iterator[Checklist]:
        return filter(predicate, self)
