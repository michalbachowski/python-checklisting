import argparse
import logging
import sys
from pathlib import PurePath
from typing import Any, Dict, Optional

from checklisting.configuration.provider import BaseConfigurationProvider, FileBasedConfigurationProvider
from checklisting.interfaces.common.loaders import BaseChecklistsLoader
from checklisting.interfaces.common.loaders.pyspd import PySPDChecklistsLoader
from checklisting.interfaces.common.runners import BaseRunner
from checklisting.interfaces.common.runners.cli import CliRunner
from checklisting.interfaces.common.runners.web import WebRunner


class ChecklistInterface(object):

    def __init__(self,
                 runner: BaseRunner,
                 configuration_provider: BaseConfigurationProvider[Dict[str, Any]],
                 checklists_loader: Optional[BaseChecklistsLoader] = None) -> None:
        self._runner = runner
        self._checklists_loader = checklists_loader or PySPDChecklistsLoader()
        self._logger = logging.getLogger('checklisting.interfaces')
        self._configuration = configuration_provider.provide_configuration()
        self._checklist_provider = self._checklists_loader.load_checklists(self._configuration)
        self._logger = self._setup_logger(self._configuration.get('debug', False))

    def _setup_logger(self, is_debug: bool) -> logging.Logger:
        level = logging.DEBUG if is_debug else logging.INFO
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(level)
        ch.setFormatter(formatter)
        logger = logging.getLogger('checklisting.interfaces')
        logger.addHandler(ch)
        logger.setLevel(level)
        return logger

    def run(self) -> None:
        self._runner.run(self._configuration, self._checklist_provider, self._logger)


def _get_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description='Checklisting CLI')
    p.add_argument('action', type=str, choices=['webserver', 'cli'], help='Action to be taken')
    p.add_argument('config', type=PurePath, help='Path to configuration file')
    return p


def main():
    args = _get_parser().parse_args()
    if args.action == 'cli':
        runner = CliRunner()
    else:
        runner = WebRunner()
    ChecklistInterface(runner, FileBasedConfigurationProvider(args.config)).run()
