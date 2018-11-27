import asyncio
import ssl
from typing import Iterator, Optional

from checklisting.result import BaseTaskResult, TaskResult
from checklisting.result.builder import MultiTaskResultBuilder
from checklisting.result.status import TaskResultStatus
from checklisting.task import BaseTask
from checklisting.tasks.socket import (BaseSocketTaskResponseValidator,
                                       SocketTask)


class ZookeeperRuokResponseValidator(BaseSocketTaskResponseValidator):

    def _validate_line(self, lineno: int, line: str) -> Iterator[BaseTaskResult]:
        if lineno == 1:
            yield TaskResult(TaskResultStatus.WARNING,
                             'Received more than 1 line from Zookeeper for [ruok] command. This was unexpected.')
        elif lineno > 1:
            return
        elif line == 'imok':
            yield TaskResult(TaskResultStatus.SUCCESS, 'Received [imok] from Zookeeper for [ruok] command')
        elif 'not in the whitelist' in line:
            yield TaskResult(TaskResultStatus.WARNING,
                             'Please add [ruok] to [4lw.commands.whitelist] property in zookeeper.conf file')
        else:
            yield TaskResult(TaskResultStatus.WARNING, f'Line [{line}] is not [imok]')


class ZookeeperMntrResonseValidator(BaseSocketTaskResponseValidator):

    def _validate_line(self, lineno: int, line: str) -> Iterator[BaseTaskResult]:
        if 'not in the whitelist' in line:
            if lineno == 0:
                yield TaskResult(TaskResultStatus.WARNING,
                                 'Please add [mntr] to [4lw.commands.whitelist] property in zookeeper.conf file')
        else:
            try:
                (key, *values) = filter(None, line.split(' '))
                yield TaskResult(TaskResultStatus.INFO, f'[{key}]=[{" ".join(values)}]')
            except ValueError:
                yield TaskResult(TaskResultStatus.WARNING, f'Line [{line}] is not parseable')


class ZookeeperTask(BaseTask):

    def __init__(self,
                 host: str,
                 port: int = 2181,
                 ssl_context: Optional[ssl.SSLContext] = None,
                 ruok_validator: Optional[BaseSocketTaskResponseValidator] = None,
                 mntr_validator: Optional[BaseSocketTaskResponseValidator] = None,
                 result_builder: Optional[MultiTaskResultBuilder] = None) -> None:
        super().__init__()
        self._ruok_task = SocketTask(b'ruok', host, port, ssl_context, ruok_validator or
                                     ZookeeperRuokResponseValidator())
        self._mntr_task = SocketTask(b'mntr', host, port, ssl_context, mntr_validator or
                                     ZookeeperMntrResonseValidator())
        self._result_builder = result_builder or MultiTaskResultBuilder()

    async def _execute(self) -> BaseTaskResult:
        return self._result_builder.of_results(await asyncio.gather(self._ruok_task.execute(),
                                                                    self._mntr_task.execute()))
