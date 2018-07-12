import logging
import sys
from typing import Optional, Union
from checklisting.output import BaseOutputWriter
from checklisting.result import BaseTaskResult
from checklisting.serializer.human import HumanReadableSerializer


class LoggingOutputWriter(BaseOutputWriter):

    DEFAULT_LOGGER_NAME = 'checklist.result'

    def __init__(self, logger: Union[logging.Logger, logging.LoggerAdapter, None] = None,
                 serializer: Optional[HumanReadableSerializer] = None) -> None:
        self._logger = logger or self._get_logger()
        self._serializer = serializer or HumanReadableSerializer()

    def _get_logger(self):
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

        logger = logging.getLogger(LoggingOutputWriter.DEFAULT_LOGGER_NAME)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        return logger

    def write(self, result: BaseTaskResult) -> None:
        for line in self._serializer.get_lines(result):
            self._logger.debug(line)
