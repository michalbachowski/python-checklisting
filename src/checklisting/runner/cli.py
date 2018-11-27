import argparse
import asyncio
from typing import Any, Dict, Optional

from checklisting.configuration.loader import ConfigurationLoader
from checklisting.loaders import (BaseChecklistsLoader,
                                  ChecklistLoaderSourceEntry)
from checklisting.loaders.pyspd import PySPDChecklistsLoader
from checklisting.output.logging import LoggingOutputWriter
from checklisting.parser import YamlParser
from checklisting.provider import BaseChecklistsProvider

from . import BaseRunner, BaseRunnerFactory


class CliRunner(BaseRunner):

    def __init__(self, checklists_provider: BaseChecklistsProvider) -> None:
        super().__init__()
        self._output_writer = LoggingOutputWriter()
        self._checklists_provider = checklists_provider

    def run(self) -> None:
        loop = asyncio.get_event_loop()
        checklists_results = loop.run_until_complete(
            asyncio.gather(*[checklist.execute() for checklist in self._checklists_provider.get_all()]))
        loop.close()

        for checklist_results in checklists_results:
            self._output_writer.write(checklist_results)


class CliRunnerFactory(BaseRunnerFactory):

    def __init__(self,
                 checklists_loader: Optional[BaseChecklistsLoader] = None,
                 configuration_loader: Optional[ConfigurationLoader[Dict[str, Any]]] = None) -> None:
        super().__init__()
        self.checklists_loader = checklists_loader or PySPDChecklistsLoader()
        self.configuration_loader = configuration_loader or \
            ConfigurationLoader[Dict[str, Any]](YamlParser[Dict[str, Any]]())

    def provide(self, args: argparse.Namespace) -> BaseRunner:
        if not args.config:
            raise RuntimeError('Please provide path to configuration file [--config]')

        raw_configuration = self.configuration_loader.load(args.config)
        return self._provide(raw_configuration)

    def _load_checklist_provider(self, raw_configuration: Dict[str, Any]) -> BaseChecklistsProvider:
        return self.checklists_loader.load_checklists(
            list(map(ChecklistLoaderSourceEntry.ofDict, raw_configuration['checklists']['sources'])),
            raw_configuration['checklists'].get('configurations', {}))

    def _provide(self, raw_configuration: Dict[str, Any]) -> BaseRunner:
        return CliRunner(self._load_checklist_provider(raw_configuration))
