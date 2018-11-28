from abc import ABC, abstractmethod
from asyncio.subprocess import PIPE, create_subprocess_exec
from logging import getLogger
from typing import Iterable

from checklisting.result import BaseTaskResult, TaskResult
from checklisting.result.status import TaskResultStatus
from checklisting.task import BaseTask

_logger = getLogger('checklisting.tasks.subprocess')


class BaseSubprocessResultValidator(ABC):

    def validate(self, stdout: str, stderr: str, exit_code: int) -> BaseTaskResult:
        try:
            return self._validate(stdout, stderr, exit_code)
        except Exception as e:
            msg = f'Could not parse subprocess result. Details:\n\nstdout:\n{stdout}\n\nstderr:\n{stderr}' + \
                  f'\n\nexit_code: {exit_code}\n\nException:\n{e}'
            _logger.exception(msg)
            return TaskResult(TaskResultStatus.UNKNOWN, msg)

    @abstractmethod
    def _validate(self, stdout: str, stderr: str, exit_code: int) -> BaseTaskResult:
        pass


class SubprocessTask(BaseTask):

    def __init__(self, command: Iterable[str], subprocess_result_validator: BaseSubprocessResultValidator,
                 charset: str = 'UTF-8') -> None:
        super().__init__()
        self._cmd = command
        self._subprocess_result_validator = subprocess_result_validator
        self._charset = charset

    async def _execute(self) -> BaseTaskResult:
        process = await create_subprocess_exec(*self._cmd, stdout=PIPE, stderr=PIPE)
        (stdout, stderr) = await process.communicate()

        return self._subprocess_result_validator.validate(
            stdout.decode(self._charset),
            stderr.decode(self._charset),
            process.returncode)
