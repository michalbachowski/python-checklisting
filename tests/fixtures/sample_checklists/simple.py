from pathlib import Path
from typing import Dict, Any
from checklisting.task import Checklist
from checklisting.interfaces.common.loaders.pyspd import PySPDChecklistProvider
from checklisting.tasks.path import FileExistsTask


class SimpleChecklistProvider(PySPDChecklistProvider):

    def get_checklist(self, configuration: Dict[str, Any]) -> Checklist:
        return Checklist("simple_checklist", [FileExistsTask(Path(__file__))])
