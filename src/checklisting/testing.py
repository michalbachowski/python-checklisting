
import asyncio
from typing import Awaitable, Callable, Tuple


class CheckType(object):

    def __init__(self, cls):
        self._cls = cls

    def __eq__(self, other):
        return isinstance(other, self._cls)

    def __repr__(self):
        return f'<{self.__class__.__name__}({self._cls.__name__})>'


class CheckGenerator(object):

    def __init__(self, expected):
        self._expected = expected

    def __eq__(self, other):
        return list(other) == self._expected

    def __repr__(self):
        return f'<generator object of: {self._expected}>'


async def _echo(reader: asyncio.StreamReader) -> bytes:
    return await reader.read(100)


async def setup_tcp_server(loop: asyncio.AbstractEventLoop,
                           response_strategy: Callable[[asyncio.StreamReader], Awaitable[bytes]] = _echo,
                           host: str = '127.0.0.1') -> Tuple[str, int]:

        async def _handler(reader, writer):
            data = await response_strategy(reader)
            writer.write(data)
            await writer.drain()
            writer.close()
        server = await asyncio.ensure_future(asyncio.start_server(_handler, host), loop=loop)
        return (host, server.sockets[0].getsockname()[1])

