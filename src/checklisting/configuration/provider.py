from abc import ABC, abstractmethod
from pathlib import PurePath
from typing import Any, Dict, Generic, Optional, TypeVar

from .loader import BaseConfigurationLoader, FileConfigurationLoader
from .parser import BaseConfigurationParser, YamlConfigurationParser

RT = TypeVar('RT')


class BaseConfigurationProvider(Generic[RT], ABC):

    @abstractmethod
    def provide_configuration(self) -> RT:
        pass


class StaticConfigurationProvider(BaseConfigurationProvider[RT]):

    def __init__(self, configuration: RT) -> None:
        self._configuration = configuration

    def provide_configuration(self) -> RT:
        return self._configuration


class ParseableConfigurationProvider(BaseConfigurationProvider[Dict[str, Any]]):

    def __init__(self, loader: BaseConfigurationLoader, parser: Optional[BaseConfigurationParser] = None) -> None:
        super().__init__()
        self._loader = loader
        self._parser = parser or YamlConfigurationParser()

    def provide_configuration(self) -> Dict[str, Any]:
        return self._parser.parse_configuration(self._loader.load_configuration())


class FileBasedConfigurationProvider(ParseableConfigurationProvider):

    def __init__(self, path: PurePath, parser: Optional[BaseConfigurationParser] = None) -> None:
        super().__init__(FileConfigurationLoader(path), parser)
