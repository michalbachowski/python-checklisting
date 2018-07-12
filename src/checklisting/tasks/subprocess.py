from abc import ABC, abstractmethod
from asyncio.subprocess import create_subprocess_exec, PIPE
from typing import Iterable
from checklisting.task import BaseTask
from checklisting.result import BaseTaskResult, TaskResult
from checklisting.result.status import TaskResultStatus


class BaseSubprocessResultValidator(ABC):

    def validate(self, stdout: str, stderr: str, exit_code: int) -> BaseTaskResult:
        try:
            return self._validate(stdout, stderr, exit_code)
        except Exception as e:
            return TaskResult(
                TaskResultStatus.UNKNOWN,
                f'Could not parse subprocess result. Details:\n\nstdout:\n{stdout}\n\nstderr:\n{stderr}\n\nexit_code: {exit_code}\n\nException:\n{e}'
            )

    @abstractmethod
    def _validate(self, stdout: str, stderr: str, exit_code: int) -> BaseTaskResult:
        pass


class SubprocessTask(BaseTask):

    def __init__(self, command: Iterable[str], subprocess_result_validator: BaseSubprocessResultValidator) -> None:
        super().__init__()
        self._cmd = command
        self._subprocess_result_validator = subprocess_result_validator

    async def _execute(self):
        process = await create_subprocess_exec(*self._cmd, stdout=PIPE, stderr=PIPE)
        (stdout, stderr) = await process.communicate()

        return self._subprocess_result_validator.validate(stdout, stderr, process.returncode)
