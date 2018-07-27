from abc import ABC, abstractmethod

from checklisting.provider import BaseChecklistsProvider


class BaseRunner(ABC):

    @abstractmethod
    def run(self, checklists_provider: BaseChecklistsProvider) -> None:
        pass
