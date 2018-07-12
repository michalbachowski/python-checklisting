from abc import ABC, abstractmethod
from checklisting.result import BaseTaskResult


class BaseSerializer(ABC):

    @abstractmethod
    def dumps(self, result: BaseTaskResult) -> str:
        pass
