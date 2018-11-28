import asyncio
from logging import getLogger
from typing import Any, Dict, Optional

from aiohttp import web

from checklisting.output.logging import LoggingOutputWriter
from checklisting.provider import BaseChecklistsProvider
from checklisting.serializer import BaseSerializer
from checklisting.serializer.json import JsonSerializer

from .. import BaseRunner
from ..cli import CliRunnerFactory

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

        return web.Response(body=self._serializer.dumps(checklists_results), content_type='application/json')


class WebserverRunner(BaseRunner):

    def __init__(self, addr: str, port: int, checklists_provider: BaseChecklistsProvider) -> None:
        super().__init__()
        self._addr = addr
        self._port = port
        self._checklists_provider = checklists_provider

    def run(self) -> None:
        handler = ChecklistHttpHandler(self._checklists_provider)
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


class WebserverRunnerFactory(CliRunnerFactory):

    def _provide(self, raw_configuration: Dict[str, Any]) -> BaseRunner:
        config = raw_configuration.get('web', {}).get('server', {})
        port = int(config.get('port', 8080))
        addr = config.get('addr', '127.0.0.1')
        return WebserverRunner(addr, port, self._load_checklist_provider(raw_configuration))
