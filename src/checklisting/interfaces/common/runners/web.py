import asyncio
from logging import Logger
from typing import Any, Dict, Iterable, Optional

from aiohttp import web

from checklisting.output.logging import LoggingOutputWriter
from checklisting.provider import BaseChecklistsProvider
from checklisting.serializer import BaseSerializer
from checklisting.serializer.json import JsonSerializer

from . import BaseRunner


class ChecklistHttpHandler(object):

    def __init__(self, checklist_provider: BaseChecklistsProvider,
                 serializer: Optional[BaseSerializer] = None) -> None:
        self._checklist_provider = checklist_provider
        self._serializer = serializer or JsonSerializer()
        self._logging_writer = LoggingOutputWriter()

    async def __call__(self, request: web.Request) -> web.Response:
        checklists_results = await asyncio.gather(*[c.execute() for c in self._checklist_provider.get_all()])

        for checklist_results in checklists_results:
            self._logging_writer.write(checklist_results)

        return web.Response(body=self._serializer.dumps(checklist_results), content_type='application/json')


def _get_host_and_port(configuration: Dict[str, Any]):
    conf = configuration.get('web', {}).get('server', {})
    return (conf.get('host', '127.0.0.1'), conf.get('port', 8080))


class WebRunner(BaseRunner):

    def run(self, configuration: Dict[str, Any], checklist_provider: BaseChecklistsProvider, logger: Logger):
        (addr, port) = _get_host_and_port(configuration)
        handler = ChecklistHttpHandler(checklist_provider)
        app = web.Application()
        app.router.add_route('GET', '/', handler)

        loop = asyncio.get_event_loop()
        future = loop.create_server(app.make_handler(), addr, port)
        srv = loop.run_until_complete(future)
        logger.info('serving on [%s]', srv.sockets[0].getsockname())
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            logger.info('shutting down')
            pass
