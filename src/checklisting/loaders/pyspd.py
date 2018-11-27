from abc import abstractmethod
from typing import Any, Dict, Iterable, Iterator

from checklisting.configuration import BaseRawConfiguration
from checklisting.provider import (BaseChecklistsProvider,
                                   StaticChecklistsProvider)
from checklisting.task import Checklist
from pyspd import MountPoint
from pyspd.loader import LoaderDir, LoaderFile, LoaderModule

from . import (BaseChecklistsLoader, ChecklistLoaderSourceEntry,
               ChecklistLoaderSourceType)


class PySPDChecklistProvider(metaclass=MountPoint):

    @abstractmethod
    def get_checklist(self, configuration: BaseRawConfiguration[Dict[str, Any]]) -> Checklist:
        pass


class PySPDChecklistsLoader(BaseChecklistsLoader[Dict[str, Any]]):

    def __init__(self):
        super().__init__()
        self._loaders = {
            ChecklistLoaderSourceType.FILE: LoaderFile(),
            ChecklistLoaderSourceType.DIRECTORY: LoaderDir(),
            ChecklistLoaderSourceType.MODULE: LoaderModule(),
        }

    def load_checklists(self, entries: Iterator[ChecklistLoaderSourceEntry],
                        configuration: BaseRawConfiguration[Dict[str, Any]]) -> BaseChecklistsProvider:
        self._load_python_sources(entries)
        return StaticChecklistsProvider(list(self._load_checklists(configuration)))

    def _load_python_sources(self, entries: Iterator[ChecklistLoaderSourceEntry]) -> None:
        for entry in entries:
            self._loaders[entry.source].load([entry.path])

    def _load_checklists(self, configuration: BaseRawConfiguration[Dict[str, Any]]) -> Iterable[Checklist]:
        for provider_class in PySPDChecklistProvider.plugins:
            yield provider_class().get_checklist(configuration)
