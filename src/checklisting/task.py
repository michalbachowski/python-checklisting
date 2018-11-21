import asyncio
from abc import ABC, abstractmethod
from typing import Iterable, Optional

from .result import BaseTaskResult, TaskResult
from .result.builder import MultiTaskResultBuilder
from .result.message.builder import PrefixedTaskResultMessageBuilder
from .result.status import TaskResultStatus


class BaseTask(ABC):

    async def execute(self) -> BaseTaskResult:
        try:
            return await self._execute()
        except Exception as e:
            return TaskResult(TaskResultStatus.FAILURE, str(e))

    @abstractmethod
    async def _execute(self) -> BaseTaskResult:
        pass


class MultiTask(BaseTask):

    def __init__(self, tasks: Iterable[BaseTask], result_builder: Optional[MultiTaskResultBuilder] = None) -> None:
        super().__init__()
        self._tasks = tasks
        self._result_builder = result_builder or MultiTaskResultBuilder()

    async def _execute(self) -> BaseTaskResult:
        results = await asyncio.gather(*[task.execute() for task in self._tasks])
        return self._result_builder.of_results(results)


class Checklist(MultiTask):

    def __init__(self, name: str, tasks: Iterable[BaseTask],
                 result_builder: Optional[MultiTaskResultBuilder] = None) -> None:
        super().__init__(
            tasks, result_builder or
            MultiTaskResultBuilder(None, PrefixedTaskResultMessageBuilder(f'Checklist [{name}]: ')))
        self._name = name

    @property
    def name(self):
        return self._name
