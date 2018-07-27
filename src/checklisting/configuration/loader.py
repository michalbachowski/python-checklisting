import io
import sys
from pathlib import PurePath
from typing import Generic, TypeVar, Union

from checklisting.parser import BaseParser

_R = TypeVar('R')


class ConfigurationLoader(Generic[_R]):

    def __init__(self, parser: BaseParser[_R]) -> None:
        super().__init__()
        self._parser = parser

    def load(self, source: Union[str, PurePath, io.BufferedIOBase, None] = None) -> _R:
        if not source:
            return self._parser.load(sys.stdin)
        if isinstance(source, io.BufferedIOBase):
            return self._parser.load(source)
        with open(source, 'r') as stream:
            return self._parser.load(stream)
