import asyncio
import unittest
from typing import Awaitable, Callable

import asynctest

from checklisting.result import MultiTaskResult, TaskResult
from checklisting.result.status import TaskResultStatus
from checklisting.tasks.services.zookeeper import (ZookeeperMntrResonseValidator,
                                                   ZookeeperRuokResponseValidator,
                                                   ZookeeperTask)
from checklisting.testing import setup_tcp_server


class ZookeeperMntrResonseValidatorTest(unittest.TestCase):

    def setUp(self) -> None:
        self._validator = ZookeeperMntrResonseValidator()

    def test_returns_one_result_for_each_line(self) -> None:
        input_lines = [b'key1 value1', b'key2 value2']
        result = self._validator.validate(input_lines)

        self.assertEqual(result.status, TaskResultStatus.INFO)
        self.assertSequenceEqual(
            result.results,
            [
                TaskResult(TaskResultStatus.INFO, '[key1]=[value1]'),
                TaskResult(TaskResultStatus.INFO, '[key2]=[value2]')
            ]
        )

    def test_returns_warning_when_command_not_on_the_whitelist(self) -> None:
        for input_line in [b'not in the whitelist', b'blah not in the whitelists.']:
            result = self._validator.validate([input_line])
            self.assertEqual(result.status, TaskResultStatus.WARNING)
            self.assertSequenceEqual(
                result.results,
                [
                    TaskResult(TaskResultStatus.WARNING,
                               'Please add [mntr] to [4lw.commands.whitelist] property in zookeeper.conf file'),
                ]
            )

    def test_returns_warning_when_command_not_on_the_whitelist_only_for_first_line(self) -> None:
        input_lines = [b'key1 value1', b'not in the whitelist']
        result = self._validator.validate(input_lines)
        self.assertEqual(result.status, TaskResultStatus.INFO)
        self.assertSequenceEqual(
            result.results,
            [
                TaskResult(TaskResultStatus.INFO, '[key1]=[value1]')
            ]
        )

    def test_returns_warning_when_command_not_on_the_whitelist_only_once(self) -> None:
        input_lines = [b'not in the whitelist', b'blah not in the whitelists.']
        result = self._validator.validate(input_lines)
        self.assertEqual(result.status, TaskResultStatus.WARNING)
        self.assertSequenceEqual(
            result.results,
            [
                TaskResult(TaskResultStatus.WARNING,
                           'Please add [mntr] to [4lw.commands.whitelist] property in zookeeper.conf file'),
            ]
        )

    def test_parses_each_line_separately(self) -> None:
        lines = [b'not in the whitelist', b'blah not in the whitelists.', b'key1 value1']
        result = self._validator.validate(lines)

        self.assertEqual(result.status, TaskResultStatus.WARNING)
        self.assertSequenceEqual(
            result.results,
            [
                TaskResult(TaskResultStatus.WARNING,
                           'Please add [mntr] to [4lw.commands.whitelist] property in zookeeper.conf file'),
                TaskResult(TaskResultStatus.INFO, '[key1]=[value1]')
            ]
        )

    def test_tries_to_parse_possibly_invalid_lines(self) -> None:
        result = self._validator.validate([b'key1value1', b'key1 value1 value2'])

        self.assertEqual(result.status, TaskResultStatus.INFO)
        self.assertEqual(result.results[0].status, TaskResultStatus.INFO)
        self.assertEqual(result.results[0].message, '[key1value1]=[]')
        self.assertEqual(result.results[1].status, TaskResultStatus.INFO)
        self.assertEqual(result.results[1].message, '[key1]=[value1 value2]')


class ZookeeperRuokResponseValidatorTest(unittest.TestCase):

    def setUp(self) -> None:
        self._validator = ZookeeperRuokResponseValidator()

    def test_returns_success_for_imok_response(self) -> None:
        input_lines = [b'imok']
        result = self._validator.validate(input_lines)

        self.assertEqual(result.status, TaskResultStatus.SUCCESS)
        self.assertSequenceEqual(
            result.results,
            [
                TaskResult(TaskResultStatus.SUCCESS, 'Received [imok] from Zookeeper for [ruok] command'),
            ]
        )

    def test_returns_warning_when_command_not_on_the_whitelist(self) -> None:
        input_lines = [b'not in the whitelist']
        result = self._validator.validate(input_lines)
        self.assertEqual(result.status, TaskResultStatus.WARNING)
        self.assertSequenceEqual(
            result.results,
            [
                TaskResult(TaskResultStatus.WARNING,
                           'Please add [ruok] to [4lw.commands.whitelist] property in zookeeper.conf file')
            ]
        )

    def test_returns_warning_when_line_is_not_imok(self) -> None:
        input_lines = [b'foo']
        result = self._validator.validate(input_lines)
        self.assertEqual(result.status, TaskResultStatus.WARNING)
        self.assertSequenceEqual(
            result.results,
            [
                TaskResult(TaskResultStatus.WARNING, 'Line [foo] is not [imok]')
            ]
        )

    def test_parses_only_first_line(self) -> None:
        input_lines = [b'imok', b'foo', b'bar', b'not in the whitelist']
        result = self._validator.validate(input_lines)

        self.assertEqual(result.status, TaskResultStatus.WARNING)
        self.assertSequenceEqual(
            result.results,
            [
                TaskResult(TaskResultStatus.SUCCESS, 'Received [imok] from Zookeeper for [ruok] command'),
                TaskResult(TaskResultStatus.WARNING,
                           'Received more than 1 line from Zookeeper for [ruok] command. This was unexpected.')
            ]
        )


def _zk_responses(ruok: bytes = b'imok', mntr: bytes = b'key1 value1\nkey2 value2') \
                  -> Callable[[asyncio.StreamReader], Awaitable[bytes]]:
    async def _handler(reader: asyncio.StreamReader) -> bytes:
        request = await reader.read(4)
        if request == b'ruok':
            return ruok
        elif request == b'mntr':
            return mntr
        return f'Unknown command [{request}]'.encode('utf-8')
    return _handler


def _zk_success_response() -> Callable[[asyncio.StreamReader], Awaitable[bytes]]:
    return _zk_responses(b'imok', b'key1 value1\nkey2 value2')


def _zk_not_on_whitelist() -> Callable[[asyncio.StreamReader], Awaitable[bytes]]:
    msg = b'Command not in the whitelist'
    return _zk_responses(msg, msg)


class ZookeeperTaskTest(asynctest.TestCase):

    async def test_successfull_responses(self) -> None:
        (host, port) = await setup_tcp_server(self.loop, _zk_success_response())

        task = ZookeeperTask(host, port)
        result = await task.execute()

        self.assertEqual(result.status, TaskResultStatus.SUCCESS)

        self.assertCountEqual(
            result.results,
            [
                MultiTaskResult(
                    TaskResultStatus.SUCCESS,
                    'Task success.',
                    [
                        TaskResult(TaskResultStatus.SUCCESS, 'Received [imok] from Zookeeper for [ruok] command')
                    ]
                ),
                MultiTaskResult(
                    TaskResultStatus.INFO,
                    'Task completed. See subtasks for details.',
                    [
                        TaskResult(TaskResultStatus.INFO, '[key1]=[value1]'),
                        TaskResult(TaskResultStatus.INFO, '[key2]=[value2]')
                    ]
                )
            ]
        )

    async def test_both_not_on_whitelist(self) -> None:
        (host, port) = await setup_tcp_server(self.loop, _zk_not_on_whitelist())

        task = ZookeeperTask(host, port)
        result = await task.execute()

        self.assertEqual(result.status, TaskResultStatus.WARNING)

        self.assertCountEqual(
            result.results,
            [
                MultiTaskResult(
                    TaskResultStatus.WARNING,
                    'Task error. See subtasks for details.',
                    [
                        TaskResult(TaskResultStatus.WARNING,
                                   'Please add [ruok] to [4lw.commands.whitelist] property in zookeeper.conf file')
                    ]
                ),
                MultiTaskResult(
                    TaskResultStatus.WARNING,
                    'Task error. See subtasks for details.',
                    [
                        TaskResult(TaskResultStatus.WARNING,
                                   'Please add [mntr] to [4lw.commands.whitelist] property in zookeeper.conf file')
                    ]
                )
            ]
        )
