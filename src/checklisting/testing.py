import asyncio
from typing import Any, Awaitable, Callable, Iterable, Iterator, Tuple, Type


class CheckType(object):

    def __init__(self, cls: Type[Any]) -> None:
        self._cls = cls

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self._cls)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}({self._cls.__name__})>'


class CheckGenerator(object):

    def __init__(self, expected: Iterator[Any]) -> None:
        self._expected = expected

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Iterable):
            return list(other) == self._expected
        return False

    def __repr__(self) -> str:
        return f'<generator object of: {self._expected}>'


async def _echo(reader: asyncio.StreamReader) -> bytes:
    return await reader.read(100)


async def setup_tcp_server(loop: asyncio.AbstractEventLoop,
                           response_strategy: Callable[[asyncio.StreamReader], Awaitable[bytes]] = _echo,
                           host: str = '127.0.0.1') -> Tuple[str, int]:

    async def _handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        data = await response_strategy(reader)
        writer.write(data)
        await writer.drain()
        writer.close()

    server = await asyncio.ensure_future(asyncio.start_server(_handler, host), loop=loop)
    return (host, server.sockets[0].getsockname()[1])
