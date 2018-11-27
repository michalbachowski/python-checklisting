from typing import Any, Dict, Optional

from checklisting.configuration import ConfigurationLoader
from checklisting.extras import import_module
from checklisting.loaders import BaseChecklistsLoader
from checklisting.provider import BaseChecklistsProvider

from .. import BaseRunner
from ..cli import CliRunnerFactory


class WebRunner(BaseRunner):

    def __init__(self, addr: str, port: int, checklists_provider: BaseChecklistsProvider) -> None:
        import_module('aiohttp')

    def run(self) -> None:
        pass


class WebRunnerFactory(CliRunnerFactory):

    def __init__(self,
                 checklists_loader: Optional[BaseChecklistsLoader] = None,
                 configuration_loader: Optional[ConfigurationLoader[Dict[str, Any]]] = None) -> None:
        super().__init__()
        import_module('aiohttp')
