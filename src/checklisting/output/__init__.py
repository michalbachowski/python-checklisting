from abc import ABC, abstractmethod
from checklisting.result import BaseTaskResult


class BaseOutputWriter(ABC):

    @abstractmethod
    def write(self, result: BaseTaskResult) -> None:
        pass
