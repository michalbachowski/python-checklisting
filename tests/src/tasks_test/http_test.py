import asyncio
from typing import Awaitable, Callable

import aiohttp
import asynctest
import mock

from checklisting.result.status import TaskResultStatus
from checklisting.tasks.http import (HttpMethod, HttpTask,
                                     SimpleHttpTaskResponseValidator)
from checklisting.testing import setup_tcp_server


def respond(msg: bytes) -> Callable[[asyncio.StreamReader], Awaitable[bytes]]:
    async def _checklist_response(reader: asyncio.StreamReader) -> bytes:
        return msg
    return _checklist_response


class HttpTaskTest(asynctest.TestCase):

    async def test_succeded_http_request(self) -> None:
        response = b'''
HTTP/1.1 200 OK
Content-Length: 0
Connection: close

'''
        (host, port) = await setup_tcp_server(self.loop, respond(response))
        url = f'http://{host}:{port}/'

        task = HttpTask(HttpMethod.GET, url)
        result = await task.execute()

        self.assertEqual(result.status, TaskResultStatus.SUCCESS)
        self.assertEqual(result.message, f'Request to [{url}] succeeded')

    async def test_failed_http_request(self) -> None:
        response = b'''
HTTP/1.1 500 Internal Server Error
Content-Length: 0
Connection: close

'''
        (host, port) = await setup_tcp_server(self.loop, respond(response))
        url = f'http://{host}:{port}/'

        task = HttpTask(HttpMethod.GET, url)
        result = await task.execute()

        self.assertEqual(result.status, TaskResultStatus.FAILURE)
        self.assertEqual(result.message, f'Request to [{url}] failed')

    async def test_client_session_is_reused(self):
        response = b'''
HTTP/1.1 200 OK
Content-Length: 0
Connection: close

'''
        (host, port) = await setup_tcp_server(self.loop, respond(response))
        url = f'http://{host}:{port}/'

        task = HttpTask(HttpMethod.GET, url)
        result1 = await task.execute()
        result2 = await task.execute()

        self.assertEqual(result1, result2)



class SimpleHttpTaskResponseValidatorTest(asynctest.TestCase):

    def setUp(self):
        self.validator = SimpleHttpTaskResponseValidator()
        self.response = mock.Mock(aiohttp.ClientResponse)
        self.url = 'test_url'
        self.response.real_url = self.url

    async def test_200_OK_means_success(self):
        self.response.status = 200

        result = await self.validator.validate(self.response)

        self.assertEqual(result.status, TaskResultStatus.SUCCESS)
        self.assertEqual(result.message, f'Request to [{self.url}] succeeded')

    async def test_non_200_OK_means_error(self):
        for status in [201, 400, 404, 500, 501]:
            self.response.status = status

            result = await self.validator.validate(self.response)

            self.assertEqual(result.status, TaskResultStatus.FAILURE)
            self.assertEqual(result.message, f'Request to [{self.url}] failed')
