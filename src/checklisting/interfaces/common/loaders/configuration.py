from pathlib import PurePath
from typing import Any, Dict
import yaml

from checklisting.interfaces.common.loaders import BaseConfigurationLoader


class YamlConfigurationLoader(BaseConfigurationLoader):

    def load_configuration(self, path: PurePath) -> Dict[str, Any]:
        with open(path, 'r') as stream:
            return yaml.load(stream)
