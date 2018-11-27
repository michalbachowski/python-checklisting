from typing import Optional

from checklisting.extras import import_module
from checklisting.provider import BaseChecklistsProvider
from checklisting.serializer import BaseSerializer

from .. import BaseRunner

ERROR_MESSAGE = 'Please install [web] extras to use checklisting.runner.web: pip install checklisting[web]'


class ChecklistHttpHandler(object):

    def __init__(self, checklist_provider: BaseChecklistsProvider,
                 serializer: Optional[BaseSerializer] = None) -> None:
        import_module('aiohttp')


class WebRunner(BaseRunner):

    def __init__(self, addr: str, port: int) -> None:
        import_module('aiohttp')

    def run(self, checklists_provider: BaseChecklistsProvider) -> None:
        pass

