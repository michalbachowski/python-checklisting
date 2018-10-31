import unittest
from typing import Iterator, List, Optional, Tuple

import asynctest

from checklisting.result import BaseTaskResult, TaskResult
from checklisting.result.status import TaskResultStatus
from checklisting.tasks.socket import BaseSocketTaskResponseValidator, SimpleSocketTaskResponseValidator, SocketTask
from checklisting.testing import setup_tcp_server


class StubSocketTaskResponseValidator(BaseSocketTaskResponseValidator):

    def __init__(self, result: Optional[BaseTaskResult] = None) -> None:
        super().__init__()
        self.lines: List[Tuple[int, str]] = []

    def _validate_line(self, lineno: int, line: str) -> Iterator[BaseTaskResult]:
        self.lines.append((lineno, line))
        yield TaskResult(TaskResultStatus.INFO, line)


class BaseSocketTaskResponseValidatorTest(unittest.TestCase):

    def setUp(self) -> None:
        self._validator = StubSocketTaskResponseValidator()

    def test_empty_lines_are_skipped(self) -> None:
        input_lines = [0, b' ', b"\t", None, b'    ', b'asd']
        self._validator.validate(input_lines)

        self.assertSequenceEqual(self._validator.lines, [(0, 'asd')])

    def test_non_bytes_are_skipped(self) -> None:
        input_lines = [0, ' ', "\t", "test1"]
        self._validator.validate(input_lines)

        self.assertSequenceEqual(self._validator.lines, [])


class SimpleSocketTaskResponseValidatorTest(unittest.TestCase):

    def setUp(self) -> None:
        self._validator = SimpleSocketTaskResponseValidator()

    def test_returns_one_result_for_each_line(self) -> None:
        input_lines = [b'test1', b'test2']
        result = self._validator.validate(input_lines)

        self.assertEqual(result.status, TaskResultStatus.INFO)
        self.assertSequenceEqual(
            result.results,
            [
                TaskResult(TaskResultStatus.INFO, 'test1'),
                TaskResult(TaskResultStatus.INFO, 'test2')
            ]
        )


class SocketTaskTest(asynctest.TestCase):

    def setUp(self) -> None:
        pass

    async def test_simple_tcp_integration(self) -> None:
        (host, port) = await setup_tcp_server(self.loop)

        task = SocketTask(b'test_request', host, port)
        result = await task.execute()

        self.assertEqual(result.status, TaskResultStatus.INFO)
        self.assertEqual(len(result.results), 1)

        sub_result = result.results.pop()
        self.assertEqual(sub_result.status, TaskResultStatus.INFO)
        self.assertEqual(sub_result.message, 'test_request')

    async def test_multiline_tcp_integration(self) -> None:
        (host, port) = await setup_tcp_server(self.loop)

        task = SocketTask(b'line1\nline2\nline3', host, port)
        result = await task.execute()

        self.assertEqual(result.status, TaskResultStatus.INFO)
        self.assertEqual(len(result.results), 3)
