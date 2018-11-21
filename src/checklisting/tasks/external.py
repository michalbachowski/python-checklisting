from typing import Any, Optional, Union

from checklisting.extras import import_module
from checklisting.result import BaseTaskResult, MultiTaskResult, TaskResult
from checklisting.result.status import TaskResultStatus
from checklisting.serializer.json import JsonDeserializer
from checklisting.tasks.http import (BaseHttpTaskResponseValidator, HttpMethod, HttpTask)

aiohttp = import_module('aiohttp')
yarl = import_module('yarl')


class ExternalChecklistResponseValidator(BaseHttpTaskResponseValidator):

    def __init__(self) -> None:
        super().__init__()
        self._deserializer = JsonDeserializer()

    async def validate(self, response: aiohttp.ClientResponse) -> BaseTaskResult:
        if response.status == 200:
            return await response.json(loads=self._deserializer.loads)
        else:
            r = MultiTaskResult(TaskResultStatus.FAILURE,
                                f'Call to external checklist [{response.real_url}] failed. See subtasks for details.',
                                [TaskResult(TaskResultStatus.INFO, await response.text())])
            return r


class ExternalChecklistTask(HttpTask):

    def __init__(self,
                 url: Union[str, yarl.URL],
                 validator: Optional[BaseHttpTaskResponseValidator] = None,
                 **kwargs: Any) -> None:
        super().__init__(HttpMethod.GET, url, validator or ExternalChecklistResponseValidator(), **kwargs)
