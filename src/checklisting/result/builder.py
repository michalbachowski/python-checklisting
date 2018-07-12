from typing import Iterator, Optional
from . import BaseTaskResult, MultiTaskResult
from .message.builder import BaseTaskResultMessageBuilder, StatusAwareTaskResultMessageBuilder
from .status.validator import BaseTaskResultStatusValidator, DefaultTaskResultStatusValidator


class MultiTaskResultBuilder(object):

    def __init__(self,
                 status_validator: Optional[BaseTaskResultStatusValidator] = None,
                 message_builder: Optional[BaseTaskResultMessageBuilder] = None) -> None:
        self._status_validator = status_validator or DefaultTaskResultStatusValidator()
        self._message_builder = message_builder or StatusAwareTaskResultMessageBuilder()

    def of_results(self, results: Iterator[BaseTaskResult]) -> MultiTaskResult:
        results_list = list(results)
        status = self._status_validator.of_results(results_list)
        message = self._message_builder.of_results(status, results_list)
        return MultiTaskResult(status, message, results_list)
