import asyncio
import ssl
from abc import ABC, abstractmethod
from enum import Enum, auto
from itertools import chain
from logging import getLogger
from typing import Iterator, List, Optional

from checklisting.result import BaseTaskResult, TaskResult, TaskResultStatus
from checklisting.result.builder import MultiTaskResultBuilder
from checklisting.task import BaseTask

logger = getLogger(__name__)


class EncodingErrorsHandling(Enum):
    STRICT = auto()
    IGNORE = auto()
    REPLACE = auto()

    def mode(self) -> str:
        return self.name.lower()


class BaseSocketTaskResponseValidator(ABC):

    def __init__(self,
                 charset: str = 'utf_8',
                 errors: EncodingErrorsHandling = EncodingErrorsHandling.STRICT,
                 result_builder: Optional[MultiTaskResultBuilder] = None) -> None:
        super().__init__()
        self._charset = charset
        self._errors = errors.mode()
        self._builder = result_builder or MultiTaskResultBuilder()

    def validate(self, lines: Iterator[bytes]) -> BaseTaskResult:
        return self._builder.of_results(
            filter(
                None,
                chain.from_iterable(
                    map(
                        lambda tpl: self._validate_line(*tpl),
                        enumerate(
                            filter(
                                None,
                                map(
                                    str.strip,
                                    map(lambda line: line.decode(self._charset, self._errors),
                                        filter(lambda line: isinstance(line, bytes), filter(None, lines))))))))))

    @abstractmethod
    def _validate_line(self, lineno: int, line: str) -> Iterator[BaseTaskResult]:
        pass


class SimpleSocketTaskResponseValidator(BaseSocketTaskResponseValidator):

    def _validate_line(self, lineno: int, line: str) -> Iterator[BaseTaskResult]:
        yield TaskResult(TaskResultStatus.INFO, line)


class SocketTask(BaseTask):

    def __init__(self,
                 cmd: bytes,
                 host: str,
                 port: int = 2181,
                 ssl_context: Optional[ssl.SSLContext] = None,
                 validator: Optional[BaseSocketTaskResponseValidator] = None) -> None:
        super().__init__()
        self._cmd = cmd
        self._host = host
        self._port = port
        self._ssl_context = ssl_context
        self._validator = validator or SimpleSocketTaskResponseValidator()

    async def _execute(self) -> BaseTaskResult:
        return self._validator.validate(await self._execute_connection())

    async def _execute_connection(self) -> Iterator[bytes]:
        logger.debug(f'Openning connection; host=[{self._host}]; port=[{self._port}]; ' +
                     f'ssl=[{self._ssl_context is not None}]')
        reader, writer = await asyncio.open_connection(self._host, self._port, ssl=self._ssl_context)
        logger.debug('Connection established')

        logger.debug(f'Sending payload; data=[{self._cmd}]')
        writer.write(self._cmd)

        logger.debug('Reading stream:')
        await writer.drain()
        output: List[bytes] = []
        while not reader.at_eof():
            data = await reader.readline()
            logger.debug('    {!r}'.format(data))
            output.append(data)

        logger.debug('Closing connection')
        writer.close()
        logger.debug('Connection closed')
        return iter(output)
