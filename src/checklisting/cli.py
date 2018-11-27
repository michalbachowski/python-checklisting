import argparse
import logging
import sys
from typing import Dict

from checklisting.runner import BaseRunnerFactory
from checklisting.runner.cli import CliRunnerFactory
from checklisting.runner.external import ExternalRunnerFactory
from checklisting.runner.webserver import WebserverRunnerFactory


def setup_logger(is_debug: bool) -> None:
    level = logging.DEBUG if is_debug else logging.INFO
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger = logging.getLogger('checklisting')
    logger.addHandler(ch)
    logger.setLevel(level)


class ChecklistingDispatcher(object):

    def __init__(self, *runner_factories: BaseRunnerFactory) -> None:
        self._runner_factories: Dict[str, BaseRunnerFactory] = dict((runner.name, runner) for runner in
                                                                    runner_factories)

    def get_parser(self) -> argparse.ArgumentParser:
        p = argparse.ArgumentParser(description='checklisting cli')
        p.add_argument('action', type=str, choices=sorted(self._runner_factories.keys()), help='action to be taken')
        # TODO: possibly allow runner factories to add own options. For now this is fine.
        p.add_argument('--config', type=str, help='path to configuration file')
        p.add_argument('--debug', action='store_true', help='turn on debugging')
        p.add_argument('-s', '--source', '--sources', dest='sources', type=str, nargs='*', action='append')
        return p

    def run(self) -> None:
        (args, remaining) = self.get_parser().parse_known_args()
        setup_logger(args.debug)
        try:
            self._runner_factories[args.action].provide(args).run()
        except KeyError:
            raise RuntimeError(f'Unknown action [{args.action}]')


def main() -> None:
    dispatcher = ChecklistingDispatcher(
        WebserverRunnerFactory(),
        CliRunnerFactory(),
        ExternalRunnerFactory()
    )
    dispatcher.run()
