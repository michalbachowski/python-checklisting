import argparse
import logging
import sys
from typing import Any, Dict, Iterator, Optional

from checklisting.configuration import BaseRawConfiguration
from checklisting.configuration.loader import ConfigurationLoader
from checklisting.loaders import BaseChecklistsLoader, BaseChecklistSourceConfiguration, ChecklistLoaderSourceEntry
from checklisting.loaders.pyspd import PySPDChecklistsLoader
from checklisting.parser import YamlParser
from checklisting.runner.factory import ChecklistingRunnerFactory, ChecklistingRunnerType
from checklisting.runner.web.config import BaseWebRunnerConfiguration

_ACTIONS = list(map(str.lower, map(str, ChecklistingRunnerType)))


class ChecklistConfiguration(BaseWebRunnerConfiguration, BaseRawConfiguration[Dict[str, Any]]):

    def __init__(self, configuration: Dict[str, Any]) -> None:
        self._raw = configuration
        self._entries = list(map(ChecklistLoaderSourceEntry.ofDict, configuration['checklists']['sources']))
        _webserver_config = self._raw.get('web', {}).get('server', {})
        self._webserver_port = int(_webserver_config.get('port', 8080))
        self._webserver_addr = _webserver_config.get('addr', '127.0.0.1')

    @property
    def checklist_sources(self) -> Iterator[ChecklistLoaderSourceEntry]:
        return self._entries

    @property
    def raw_config(self) -> Dict[str, Any]:
        return self._raw

    @property
    def sources_configuration(self) -> BaseChecklistSourceConfiguration:
        return self._raw['checklists'].get('configurations', {})

    @property
    def webserver_port(self) -> int:
        return self._webserver_port

    @property
    def webserver_addr(self) -> str:

        return self._webserver_addr


def get_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description='Checklisting CLI')
    p.add_argument('action', type=str, choices=_ACTIONS, help='Action to be taken')
    p.add_argument('config', type=str, help='Path to configuration file')
    p.add_argument('--debug', action='store_true', help='Turn on debugging')
    return p


def setup_logger(is_debug: bool) -> None:
    level = logging.DEBUG if is_debug else logging.INFO
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger = logging.getLogger('checklisting')
    logger.addHandler(ch)
    logger.setLevel(level)


def run(checklists_loader: Optional[BaseChecklistsLoader] = None,
        configuration_loader: Optional[ConfigurationLoader[Dict[str, Any]]] = None,
        runner_factory: ChecklistingRunnerFactory = None):
    checklists_loader = checklists_loader or PySPDChecklistsLoader()
    configuration_loader = configuration_loader or ConfigurationLoader[Dict[str, Any]](YamlParser[Dict[str, Any]]())
    runner_factory = runner_factory or ChecklistingRunnerFactory()

    args = get_parser().parse_args()
    setup_logger(args.debug)
    raw_configuration = configuration_loader.load(args.config)
    configuration = ChecklistConfiguration(raw_configuration)
    checklists_provider = checklists_loader.load_checklists(configuration.checklist_sources,
                                                            configuration.sources_configuration)
    runner = runner_factory.create_runner(ChecklistingRunnerType.ofString(args.action), configuration)
    runner.run(checklists_provider)


def main():
    run()
