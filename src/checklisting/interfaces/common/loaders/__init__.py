from abc import ABC, abstractmethod
from typing import Any, Dict

from checklisting.provider import BaseChecklistsProvider


class BaseChecklistsLoader(ABC):

    @abstractmethod
    def load_checklists(self, configuration: Dict[str, Any]) -> BaseChecklistsProvider:
        pass
