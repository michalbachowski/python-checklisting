import asyncio
from logging import Logger
from typing import Any, Dict, Iterable

from checklisting.output.logging import LoggingOutputWriter
from checklisting.task import Checklist

from . import BaseRunner


class CliRunner(BaseRunner):

    def __init__(self) -> None:
        super().__init__()
        self._output_writer = LoggingOutputWriter()

    def run(self, configuration: Dict[str, Any], checklists: Iterable[Checklist], logger: Logger) -> None:
        loop = asyncio.get_event_loop()
        checklists_results = loop.run_until_complete(
            asyncio.gather(*[checklist.execute() for checklist in checklists]))
        loop.close()

        for checklist_results in checklists_results:
            self._output_writer.write(checklist_results)
