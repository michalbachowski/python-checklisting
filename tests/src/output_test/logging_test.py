import logging
import mock
import unittest
from checklisting.output.logging import LoggingOutputWriter
from checklisting.result import TaskResult, MultiTaskResult
from checklisting.result.status import TaskResultStatus
from checklisting.serializer.human import HumanReadableSerializer


class LoggingOutputWriterTest(unittest.TestCase):

    def setUp(self):
        self.serializer = mock.Mock(HumanReadableSerializer)
        self.serializer.get_lines.return_value = ['serializer_result']
        self.logger = mock.Mock(logging.LoggerAdapter)
        self.writer = LoggingOutputWriter(self.logger, self.serializer)

    def test_defaults(self):
        msg1 = 'message1'
        result1 = TaskResult(TaskResultStatus.SUCCESS, msg1)

        msg2 = 'message2'
        result2 = TaskResult(TaskResultStatus.INFO, msg2)

        msg_multi = 'multi message'
        status_multi = TaskResultStatus.FAILURE
        multi = MultiTaskResult(status_multi, msg_multi, [result1, result2])
        self.writer.write(multi)

        writer = LoggingOutputWriter()
        with self.assertLogs(level=logging.DEBUG, logger=LoggingOutputWriter.DEFAULT_LOGGER_NAME) as logger:
            writer.write(multi)
            self.assertListEqual(logger.output, [
                'DEBUG:checklist.result:[FAILURE ] multi message',
                'DEBUG:checklist.result:    [SUCCESS ] message1',
                'DEBUG:checklist.result:    [INFO    ] message2',
            ])

    def test_unknown_result(self):
        msg = 'unknown_message'
        result = TaskResult(TaskResultStatus.UNKNOWN, msg)

        self.writer.write(result)

        self.serializer.get_lines.assert_valled_once_with(result)
        self.logger.debug.assert_called_once_with('serializer_result')

    def test_multi_result(self):
        msg1 = 'unknown_message'
        result1 = TaskResult(TaskResultStatus.SUCCESS, msg1)

        msg2 = 'unknown_message'
        result2 = TaskResult(TaskResultStatus.INFO, msg2)

        msg_multi = 'multi message'
        status_multi = TaskResultStatus.FAILURE
        multi = MultiTaskResult(status_multi, msg_multi, [result1, result2])
        self.writer.write(multi)

        self.serializer.get_lines.assert_valled_once_with(multi)
