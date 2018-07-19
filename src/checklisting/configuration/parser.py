import io
from abc import ABC, abstractmethod
from typing import Any, Dict

import yaml


class BaseConfigurationParser(ABC):

    @abstractmethod
    def parse_configuration(self, stream: io.BufferedIOBase) -> Dict[str, Any]:
        pass


class YamlConfigurationParser(BaseConfigurationParser):

    def parse_configuration(self, stream: io.BufferedIOBase) -> Dict[str, Any]:
        return yaml.load(stream)
