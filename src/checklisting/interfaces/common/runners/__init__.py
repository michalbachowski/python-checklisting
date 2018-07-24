from abc import ABC, abstractmethod
from logging import Logger
from typing import Any, Dict, Iterable

from checklisting.task import Checklist


class BaseRunner(ABC):

    @abstractmethod
    def run(self, configuration: Dict[str, Any], checklists: Iterable[Checklist], logger: Logger) -> None:
        pass
