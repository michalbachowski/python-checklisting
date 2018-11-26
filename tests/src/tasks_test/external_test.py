import asyncio
from typing import Awaitable, Callable, Optional

import aiohttp
import asynctest
import mock

from checklisting.result import BaseTaskResult, MultiTaskResult, TaskResult
from checklisting.result.status import TaskResultStatus
from checklisting.serializer.json import JsonSerializer
from checklisting.tasks.external import (ExternalChecklistResponseValidator,
                                         ExternalChecklistTask)
from checklisting.testing import setup_tcp_server


def respond(msg: str) -> Callable[[asyncio.StreamReader], Awaitable[bytes]]:

    async def _checklist_response(reader: asyncio.StreamReader) -> bytes:
        return msg.encode('utf-8')

    return _checklist_response


class ExternalChecklistTaskTest(asynctest.TestCase):

    def setUp(self) -> None:
        self._serializer = JsonSerializer()

    async def _do_test(self, results: BaseTaskResult, error_results: Optional[BaseTaskResult] = None) -> None:
        if not error_results:
            status = '200 OK'
        else:
            status = '500 Internal Server Error'
        response_json = self._serializer.dumps(results)

        response = f'''
HTTP/1.1 {status}
Content-Type: application/json
Connection: Closed

{response_json}'''
        (host, port) = await setup_tcp_server(self.loop, respond(response))
        url = f'http://{host}:{port}/'

        task = ExternalChecklistTask(url)
        received_result = await task.execute()

        self.assertEqual(received_result, error_results or results)

    async def test_succeded_http_request_with_success_response(self) -> None:
        await self._do_test(TaskResult(TaskResultStatus.SUCCESS, 'test_message'))

    async def test_succeded_http_request_with_error_results(self) -> None:
        await self._do_test(TaskResult(TaskResultStatus.FAILURE, 'test_message'))

    async def test_error_http_request_with_error_results(self) -> None:
        res = TaskResult(TaskResultStatus.SUCCESS, 'test_message')
        await self._do_test(
            res,
            MultiTaskResult(TaskResultStatus.FAILURE, mock.ANY,
                            [TaskResult(TaskResultStatus.INFO, self._serializer.dumps(res))]))


class ExternalChecklistResponseValidatorTest(asynctest.TestCase):

    def setUp(self) -> None:
        self._validator = ExternalChecklistResponseValidator()
        self._response = mock.Mock(aiohttp.ClientResponse)
        self._response.status = 200
        self._response_dict = dict(test_key='test_value')
        self._response.json = asynctest.CoroutineMock(return_value=self._response_dict)
        self._response.text = asynctest.CoroutineMock(return_value='test_text')

    async def test_for_status_200_returns_parsed_json_as_is(self) -> None:
        self.assertIs(self._response_dict, await self._validator.validate(self._response))

    async def test_for_status_other_than_200_returns_response_containing_response_test(self) -> None:
        self._response.status = 201

        result = await self._validator.validate(self._response)

        self.assertEqual(result.status, TaskResultStatus.FAILURE)
        self.assertIn('Call to external checklist', result.message)

        inner_result = result.results[0]
        self.assertEqual(inner_result.status, TaskResultStatus.INFO)
        self.assertEqual(inner_result.message, 'test_text')
