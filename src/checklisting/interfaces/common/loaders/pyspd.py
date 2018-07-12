from abc import abstractmethod
from typing import Any, Dict, Iterable, Iterator

from checklisting.interfaces.common.loaders import BaseChecklistsLoader
from checklisting.provider import BaseChecklistsProvider, StaticChecklistsProvider
from checklisting.task import Checklist
from pyspd import MountPoint
from pyspd.loader import LoaderFile


class PySPDChecklistProvider(metaclass=MountPoint):

    @abstractmethod
    def get_checklist(self, configuration: Dict[str, Any]) -> Checklist:
        pass


class PySPDChecklistsLoader(BaseChecklistsLoader):

    TOP_LEVEL_KEY_NAME = 'pyspd_providers'
    FILE_LIST_KEY_NAME = 'files'

    def __init__(self):
        super().__init__()
        self._loaded = []
        self._file_loader = LoaderFile()

    def load_checklists(self, configuration: Dict[str, Any]) -> BaseChecklistsProvider:
        self._load_files(configuration[PySPDChecklistsLoader.TOP_LEVEL_KEY_NAME])
        return StaticChecklistsProvider(list(self._load_checklists(configuration)))

    def _load_files(self, configuration: Dict[str, Dict[str, Iterator[str]]]) -> None:
        self._file_loader.load(configuration[PySPDChecklistsLoader.FILE_LIST_KEY_NAME])

    def _load_checklists(self, configuration: Dict[str, Any]) -> Iterable[Checklist]:
        for provider_class in PySPDChecklistProvider.plugins:
            if provider_class not in self._loaded:
                self._loaded.append(provider_class)
                yield provider_class().get_checklist(configuration)
