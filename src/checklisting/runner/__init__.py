from abc import ABC, abstractmethod
from logging import Logger
from typing import Any, Dict

from checklisting.provider import BaseChecklistsProvider


class BaseRunner(ABC):

    @abstractmethod
    def run(self, configuration: Dict[str, Any], checklists_provider: BaseChecklistsProvider, logger: Logger) -> None:
        pass
