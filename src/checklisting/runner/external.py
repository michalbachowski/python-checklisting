import argparse
from itertools import chain
from typing import Iterator

from checklisting.output.logging import LoggingOutputWriter

from . import BaseRunner, BaseRunnerFactory


class ExternalChecklistRunner(BaseRunner):

    def __init__(self, sources: Iterator[str]) -> None:
        super().__init__()
        self._output_writer = LoggingOutputWriter()
        self._sources = list(sources)

    def run(self) -> None:
        print(self._sources)


class ExternalRunnerFactory(BaseRunnerFactory):

    def __init__(self) -> None:
        super().__init__()

    def provide(self, args: argparse.Namespace) -> BaseRunner:
        if not args.sources:
            raise RuntimeError('Please provide external sources to checklist [-s | --source | --sources]')

        sources = list(
            filter(
                None,
                chain.from_iterable(
                    filter(
                        None,
                        map(
                            lambda item: item.split(','),
                            chain.from_iterable(args.sources))))))
        return ExternalChecklistRunner(sources)
