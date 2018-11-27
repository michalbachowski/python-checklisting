from __future__ import annotations

import logging
from enum import Enum, auto

from . import BaseRunner
from .cli import CliRunner
from .web import WebRunner
from .web.config import BaseWebRunnerConfiguration


class ChecklistingRunnerType(Enum):
    CLI = auto()
    WEBSERVER = auto()

    @classmethod
    def ofString(cls, name: str) -> ChecklistingRunnerType:
        return cls[name.upper()]

    def __str__(self):
        return self.name


class ChecklistingRunnerFactory(object):

    def create_runner(self, action: ChecklistingRunnerType, configuration: BaseWebRunnerConfiguration) -> BaseRunner:
        if action == ChecklistingRunnerType.CLI:
            return CliRunner()
        if action == ChecklistingRunnerType.WEBSERVER:
            return WebRunner(configuration.webserver_addr, configuration.webserver_port)
        raise RuntimeError(f'Unsupported action [{action}]')

