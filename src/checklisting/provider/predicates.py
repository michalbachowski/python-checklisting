from abc import abstractmethod
from typing import Container, Callable
from checklisting.task import Checklist


class BaseChecklistsFilterPredicate(Callable[[Checklist], bool]):

    @abstractmethod
    def __call__(self, checklist: Checklist) -> bool:
        pass


class AllowAllChecklistsFilterPredicate(BaseChecklistsFilterPredicate):

    def __call__(self, checklist: Checklist) -> bool:
        return True


class WhitelistChecklistFilterPredicate(BaseChecklistsFilterPredicate):

    def __init__(self, allowed_names: Container) -> None:
        self._allowed_names = allowed_names

    def __call__(self, checklist: Checklist) -> bool:
        return checklist.name in self._allowed_names
