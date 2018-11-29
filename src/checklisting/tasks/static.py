from checklisting.result import BaseTaskResult
from checklisting.task import BaseTask


class StaticResultTask(BaseTask):

    def __init__(self, result: BaseTaskResult) -> None:
        super().__init__()
        self._result = result

    async def _execute(self) -> BaseTaskResult:
        return self._result
