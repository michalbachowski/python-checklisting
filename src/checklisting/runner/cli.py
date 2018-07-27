import asyncio

from checklisting.output.logging import LoggingOutputWriter
from checklisting.provider import BaseChecklistsProvider

from . import BaseRunner


class CliRunner(BaseRunner):

    def __init__(self) -> None:
        super().__init__()
        self._output_writer = LoggingOutputWriter()

    def run(self, checklists_provider: BaseChecklistsProvider) -> None:
        loop = asyncio.get_event_loop()
        checklists_results = loop.run_until_complete(
            asyncio.gather(*[checklist.execute() for checklist in checklists_provider.get_all()]))
        loop.close()

        for checklist_results in checklists_results:
            self._output_writer.write(checklist_results)
