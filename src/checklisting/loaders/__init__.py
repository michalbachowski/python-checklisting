from abc import ABC, abstractmethod
from enum import Enum
from pathlib import PurePath
from typing import Any, Dict, Generic, Iterator, NewType, TypeVar, Union

from checklisting.provider import BaseChecklistsProvider

_C = TypeVar('C')


class ChecklistLoaderSourceType(Enum):
    FILE = 'file'
    DIRECTORY = 'directory'
    MODULE = 'module'

    # TODO: unqute return type once py36 compatibility is dropped
    @classmethod
    def ofString(cls, name: str) -> 'ChecklistLoaderSourceType':
        return cls[name.upper()]

    def __str__(self):
        return self.name


class ChecklistLoaderSourceEntry(object):

    def __init__(self, source: ChecklistLoaderSourceType, path: PurePath) -> None:
        self._source = source
        self._path = path

    # TODO: unqute return type once py36 compatibility is dropped
    @staticmethod
    def ofDict(dictionary: Dict[str, Union[PurePath, ChecklistLoaderSourceType]]) -> 'ChecklistLoaderEntry':
        return ChecklistLoaderSourceEntry(
            ChecklistLoaderSourceType.ofString(dictionary['type']), PurePath(dictionary['path']))

    @property
    def source(self) -> ChecklistLoaderSourceType:
        return self._source

    @property
    def path(self) -> PurePath:
        return self._path


BaseChecklistSourceConfiguration = NewType('BaseChecklistSourceConfiguration', Dict[str, Any])


class BaseChecklistsLoader(Generic[_C], ABC):

    @abstractmethod
    def load_checklists(self, entries: Iterator[ChecklistLoaderSourceEntry],
                        configuration: BaseChecklistSourceConfiguration) -> BaseChecklistsProvider:
        pass
