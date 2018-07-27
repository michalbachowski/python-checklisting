from pathlib import Path

from checklisting.loaders import BaseChecklistSourceConfiguration
from checklisting.loaders.pyspd import PySPDChecklistProvider
from checklisting.task import Checklist
from checklisting.tasks.path import FileExistsTask


class SimpleChecklistProvider(PySPDChecklistProvider):

    def get_checklist(self, configuration: BaseChecklistSourceConfiguration) -> Checklist:
        return Checklist("simple_checklist", [FileExistsTask(Path(__file__))])
