from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Union

from .status import TaskResultStatus


class BaseTaskResult(ABC):

    @property
    @abstractmethod
    def status(self) -> TaskResultStatus:
        pass

    @property
    @abstractmethod
    def message(self) -> str:
        pass

    def __repr__(self):
        return f'<{self.__class__.__name__}({self.status}, "{self.message[:20]}...")>'

    def __eq__(self, other: BaseTaskResult) -> bool:
        return self.status == other.status and self.message == other.message


class TaskResult(BaseTaskResult):

    def __init__(self, status: TaskResultStatus, message: str) -> None:
        super().__init__()
        self._status = status
        self._message = message

    @property
    def status(self) -> TaskResultStatus:
        return self._status

    @property
    def message(self) -> str:
        return self._message


class MultiTaskResult(TaskResult):

    def __init__(self, status: TaskResultStatus, message: str, task_results: Iterable[BaseTaskResult]) -> None:
        super().__init__(status, message)
        self._results = list(task_results)

    @property
    def results(self) -> Iterable[BaseTaskResult]:
        return self._results

    def __eq__(self, other: Union[BaseTaskResult, MultiTaskResult]) -> bool:
        if not super().__eq__(other):
            return False
        if not isinstance(other, MultiTaskResult):
            return True
        return self._results == other.results
