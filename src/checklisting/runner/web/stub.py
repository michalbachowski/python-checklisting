from typing import Optional

from checklisting.provider import BaseChecklistsProvider
from checklisting.serializer import BaseSerializer

from .. import BaseRunner

ERROR_MESSAGE = 'Please install [web] extras to use checklisting.runner.web: pip install checklisting[web]'


class ChecklistHttpHandler(object):

    def __init__(self, checklist_provider: BaseChecklistsProvider,
                 serializer: Optional[BaseSerializer] = None) -> None:
        raise RuntimeError(ERROR_MESSAGE)


class WebRunner(BaseRunner):

    def __init__(self, addr: str, port: int) -> None:
        raise RuntimeError(ERROR_MESSAGE)

    def run(self, checklists_provider: BaseChecklistsProvider) -> None:
        pass
