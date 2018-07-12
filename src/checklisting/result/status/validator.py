from abc import ABC, abstractmethod
from collections import Counter
from typing import Callable, Iterable

from checklisting.result import BaseTaskResult
from checklisting.result.status import TaskResultStatus


class BaseTaskResultStatusValidator(ABC):

    def of_results(self, results: Iterable[BaseTaskResult]) -> TaskResultStatus:
        return self.validate([result.status for result in results])

    @abstractmethod
    def validate(self, task_result_statuses: Iterable[TaskResultStatus]) -> TaskResultStatus:
        pass


class FallbackTaskResultStatusValidator(BaseTaskResultStatusValidator):

    def __init__(self, fallback: Callable[[], TaskResultStatus],
                 inner_validator: BaseTaskResultStatusValidator) -> None:
        super().__init__()
        self._fallback = fallback
        self._inner_validator = inner_validator

    def validate(self, task_result_statuses: Iterable[TaskResultStatus]) -> TaskResultStatus:
        result = self._inner_validator.validate(task_result_statuses)
        if result != TaskResultStatus.UNKNOWN:
            return result
        return self._fallback()


class AllOfSameTypeTaskResultStatusValidator(BaseTaskResultStatusValidator):

    def validate(self, task_result_statuses: Iterable[TaskResultStatus]) -> TaskResultStatus:
        if not task_result_statuses:
            return TaskResultStatus.UNKNOWN

        statuses = set(task_result_statuses)

        if len(statuses) == 1:
            return statuses.pop()

        return TaskResultStatus.UNKNOWN


class MostCommonTaskResultStatusValidator(BaseTaskResultStatusValidator):

    def validate(self, task_result_statuses: Iterable[TaskResultStatus]) -> TaskResultStatus:
        if not task_result_statuses:
            return TaskResultStatus.UNKNOWN

        statuses = Counter(task_result_statuses)
        most_common_statuses = statuses.most_common(2)

        try:
            (most_common, second_most_common) = most_common_statuses
            if most_common[1] == second_most_common[1]:
                return TaskResultStatus.UNKNOWN
        except ValueError:
            most_common = most_common_statuses.pop()

        return most_common[0]


class AvailableStatusTaskResultStatusValidator(BaseTaskResultStatusValidator):

    def __init__(self, expected_status: TaskResultStatus) -> None:
        super().__init__()
        self._expected_status = expected_status

    def validate(self, task_result_statuses: Iterable[TaskResultStatus]) -> TaskResultStatus:
        if not task_result_statuses:
            return TaskResultStatus.UNKNOWN

        if self._expected_status in task_result_statuses:
            return self._expected_status

        return TaskResultStatus.UNKNOWN


class AggregatedTaskResultStatusValidator(BaseTaskResultStatusValidator):

    def __init__(self, *inner_validators: Iterable[BaseTaskResultStatusValidator]) -> None:
        super().__init__()
        self._inner_validators = inner_validators

    def validate(self, task_result_statuses: Iterable[TaskResultStatus]) -> TaskResultStatus:
        for validator in self._inner_validators:
            result = validator.validate(task_result_statuses)
            if result != TaskResultStatus.UNKNOWN:
                return result

        return TaskResultStatus.UNKNOWN


class PrioritizedTaskResultStatusValidator(AggregatedTaskResultStatusValidator):

    def __init__(self):
        super().__init__(
            AvailableStatusTaskResultStatusValidator(TaskResultStatus.FAILURE),
            AvailableStatusTaskResultStatusValidator(TaskResultStatus.WARNING),
            AvailableStatusTaskResultStatusValidator(TaskResultStatus.SUCCESS),
            AvailableStatusTaskResultStatusValidator(TaskResultStatus.INFO),
            AvailableStatusTaskResultStatusValidator(TaskResultStatus.UNKNOWN),
        )


class DefaultTaskResultStatusValidator(AggregatedTaskResultStatusValidator):

    def __init__(self):
        super().__init__(
            AllOfSameTypeTaskResultStatusValidator(),
            PrioritizedTaskResultStatusValidator(),
        )
