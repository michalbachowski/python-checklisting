import asyncio
from logging import getLogger
from typing import Optional

from aiohttp import web

from checklisting.output.logging import LoggingOutputWriter
from checklisting.provider import BaseChecklistsProvider
from checklisting.serializer import BaseSerializer
from checklisting.serializer.json import JsonSerializer

from .. import BaseRunner

_logger = getLogger('checklisting.runner.web')


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


class WebRunner(BaseRunner):

    def __init__(self, addr: str, port: int) -> None:
        super().__init__()
        self._addr = addr
        self._port = port

    def run(self, checklists_provider: BaseChecklistsProvider) -> None:
        handler = ChecklistHttpHandler(checklists_provider)
        app = web.Application()
        app.router.add_route('GET', '/', handler)

        loop = asyncio.get_event_loop()
        future = loop.create_server(app.make_handler(), self._addr, self._port)
        srv = loop.run_until_complete(future)
        _logger.info('serving on [%s]', srv.sockets[0].getsockname())
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            _logger.info('shutting down')
            pass

