from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Awaitable, Optional, Union

from checklisting.extras import import_module
from checklisting.result import BaseTaskResult, TaskResult
from checklisting.result.status import TaskResultStatus
from checklisting.task import BaseTask

aiohttp = import_module('aiohttp')
yarl = import_module('yarl')


class HttpMethod(Enum):

    CONNECT = aiohttp.hdrs.METH_CONNECT
    HEAD = aiohttp.hdrs.METH_HEAD
    GET = aiohttp.hdrs.METH_GET
    DELETE = aiohttp.hdrs.METH_DELETE
    OPTIONS = aiohttp.hdrs.METH_OPTIONS
    PATCH = aiohttp.hdrs.METH_PATCH
    POST = aiohttp.hdrs.METH_POST
    PUT = aiohttp.hdrs.METH_PUT
    TRACE = aiohttp.hdrs.METH_TRACE


class BaseHttpTaskResponseValidator(ABC):

    @abstractmethod
    async def validate(self, response: aiohttp.ClientResponse) -> Awaitable[BaseTaskResult]:
        pass


class SimpleHttpTaskResponseValidator(BaseHttpTaskResponseValidator):

    async def validate(self, response: aiohttp.ClientResponse) -> Awaitable[BaseTaskResult]:
        if response.status == 200:
            return TaskResult(TaskResultStatus.SUCCESS, f'Request to [{response.real_url}] succeeded')
        return TaskResult(TaskResultStatus.FAILURE, f'Request to [{response.real_url}] failed')


class HttpTask(BaseTask):

    def __init__(self,
                 method: HttpMethod,
                 url: Union[str, yarl.URL],
                 validator: Optional[BaseHttpTaskResponseValidator] = None,
                 **kwargs: Any) -> None:
        super().__init__()
        self._method = method
        self._url = url
        self._kwargs = kwargs
        self._client_session = None
        self._validator = validator or SimpleHttpTaskResponseValidator()

    async def _execute(self) -> BaseTaskResult:
        async with aiohttp.ClientSession() as session:
            async with session.request(self._method.value, self._url, **self._kwargs) as resp:
                return await self._validator.validate(resp)
