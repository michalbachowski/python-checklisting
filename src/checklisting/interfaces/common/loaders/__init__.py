from abc import ABC, abstractmethod
from pathlib import PurePath
from typing import Any, Dict
from checklisting.provider import BaseChecklistsProvider


class BaseChecklistsLoader(ABC):

    @abstractmethod
    def load_checklists(self, configuration: Dict[str, Any]) -> BaseChecklistsProvider:
        pass


class BaseConfigurationLoader(ABC):

    @abstractmethod
    def load_configuration(self, path: PurePath) -> Dict[str, Any]:
        pass
