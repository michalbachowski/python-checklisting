# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import Iterator, Optional

from .. import BaseTaskResult
from ..status import TaskResultStatus


class BaseTaskResultMessageBuilder(ABC):

    def of_results(self, status: TaskResultStatus, results: Iterator[BaseTaskResult]) -> TaskResultStatus:
        return self.build(status, [result.message for result in results])

    @abstractmethod
    def build(self, status: TaskResultStatus, messages: Iterator[str]) -> str:
        pass


class StatusAwareTaskResultMessageBuilder(BaseTaskResultMessageBuilder):

    def build(self, status: TaskResultStatus, messages: Iterator[str]) -> str:
        if status == TaskResultStatus.FAILURE:
            return 'Task failure. See subtasks for details.'

        if status == TaskResultStatus.WARNING:
            return 'Task error. See subtasks for details.'

        if status == TaskResultStatus.SUCCESS:
            return 'Task success.'

        if status == TaskResultStatus.UNKNOWN:
            return 'Task is in unknown state. See subtasks for details.'

        return 'Task completed. See subtasks for details.'


class PrefixedTaskResultMessageBuilder(BaseTaskResultMessageBuilder):

    def __init__(self, prefix: str, inner_builder: Optional[BaseTaskResultMessageBuilder] = None) -> None:
        super().__init__()
        self._prefix = prefix
        self._inner_builder = inner_builder or StatusAwareTaskResultMessageBuilder()

    def build(self, status: TaskResultStatus, messages: Iterator[str]) -> str:
        msg = self._inner_builder.build(status, messages)
        return f'{self._prefix}{msg}'
