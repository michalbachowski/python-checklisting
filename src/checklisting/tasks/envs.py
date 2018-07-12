from os import environ
from checklisting.task import BaseTask
from checklisting.result import BaseTaskResult, TaskResult
from checklisting.result.status import TaskResultStatus


class CheckEnvironmentVariableTask(BaseTask):

    def __init__(self, variable_name: str) -> None:
        super().__init__()
        self._variable_name = variable_name
        self._msg_prefix = f'Environment variable [{self._variable_name}]'

    async def _execute(self) -> BaseTaskResult:
        if self._variable_name not in environ:
            return TaskResult(TaskResultStatus.FAILURE, f'{self._msg_prefix} not found.')

        return TaskResult(TaskResultStatus.SUCCESS, f'{self._msg_prefix} has value [{environ[self._variable_name]}]')
