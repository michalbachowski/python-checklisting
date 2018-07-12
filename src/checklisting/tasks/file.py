from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterator, Optional
from checklisting.task import BaseTask
from checklisting.result import BaseTaskResult, TaskResult
from checklisting.result.builder import MultiTaskResultBuilder
from checklisting.result.status import TaskResultStatus


class BaseFileContentValidator(ABC):

    @abstractmethod
    def validate(self, lines: Iterator[str]) -> BaseTaskResult:
        pass


class BaseLineValidator(ABC):

    @abstractmethod
    def validate(self, line: str) -> Optional[BaseTaskResult]:
        pass


class PerLineFileContentValidator(BaseFileContentValidator):

    def __init__(self, line_validator: BaseLineValidator,
                 result_builder: Optional[MultiTaskResultBuilder] = None) -> None:
        super().__init__()
        self._line_validator = line_validator
        self._result_builder = result_builder or MultiTaskResultBuilder()

    def validate(self, lines: Iterator[str]) -> BaseTaskResult:
        return self._result_builder.of_results(
            filter(None, map(self._line_validator.validate, filter(None, map(str.strip, filter(None, lines))))))


class FileContentTask(BaseTask):

    def __init__(self, path: Path, validator: BaseFileContentValidator) -> None:
        super().__init__()
        self._path = path
        self._validator = validator

    async def _execute(self) -> BaseTaskResult:
        if not self._path.exists():
            return TaskResult(TaskResultStatus.FAILURE, f'File [{self._path}] does not exist')

        with open(self._path, 'r', 1) as stream:
            return self._validator.validate(stream)
