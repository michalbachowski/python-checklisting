import argparse
from itertools import chain
from typing import Iterator

from checklisting.extras import import_module
from checklisting.provider import StaticChecklistsProvider
from checklisting.task import Checklist
from checklisting.tasks.external import ExternalChecklistTask

from . import BaseRunner, BaseRunnerFactory
from .cli import CliRunner

yarl = import_module('yarl')


def _fix_url(source: str) -> str:
    if not source.startswith('http'):
        return f'http://{source}'
    else:
        return source


class ExternalChecklistRunner(CliRunner):

    def __init__(self, sources: Iterator[yarl.URL]) -> None:
        super().__init__(
            StaticChecklistsProvider([Checklist('external', (ExternalChecklistTask(source) for source in sources))]))


class ExternalChecklistRunnerFactory(BaseRunnerFactory):

    def __init__(self) -> None:
        super().__init__()

    @property
    def name(self) -> str:
        return 'external'

    def provide(self, args: argparse.Namespace) -> BaseRunner:
        if not args.sources:
            raise RuntimeError('Please provide external sources to checklist [-s | --source | --sources]')

        sources = list(
            map(
                yarl.URL,
                map(
                    _fix_url,
                    filter(
                        None,
                        chain.from_iterable(
                            filter(None, map(lambda item: item.split(','), chain.from_iterable(args.sources))))))))
        return ExternalChecklistRunner(sources)
