import unittest
import mock
from checklisting.result import TaskResult, MultiTaskResult
from checklisting.result.status import TaskResultStatus
from checklisting.serializer.json import JsonSerializer


class JsonSerializerTest(unittest.TestCase):

    def setUp(self):
        self.serializer = JsonSerializer()

    def test_success_result(self):
        msg = 'success_message'
        result = TaskResult(TaskResultStatus.SUCCESS, msg)

        self.assertEqual(self.serializer.dumps(result), f'{{"status": "SUCCESS", "message": "{msg}"}}')

    def test_failure_result(self):
        msg = 'failure_message'
        result = TaskResult(TaskResultStatus.FAILURE, msg)

        self.assertEqual(self.serializer.dumps(result), f'{{"status": "FAILURE", "message": "{msg}"}}')

    def test_warning_result(self):
        msg = 'warning_message'
        result = TaskResult(TaskResultStatus.WARNING, msg)

        self.assertEqual(self.serializer.dumps(result), f'{{"status": "WARNING", "message": "{msg}"}}')

    def test_info_result(self):
        msg = 'info_message'
        result = TaskResult(TaskResultStatus.INFO, msg)

        self.assertEqual(self.serializer.dumps(result), f'{{"status": "INFO", "message": "{msg}"}}')

    def test_unknown_result(self):
        msg = 'unknown_message'
        result = TaskResult(TaskResultStatus.UNKNOWN, msg)

        self.assertEqual(self.serializer.dumps(result), f'{{"status": "UNKNOWN", "message": "{msg}"}}')

    def test_multi_result(self):
        msg1 = 'message1'
        result1 = TaskResult(TaskResultStatus.SUCCESS, msg1)

        msg2 = 'message2'
        result2 = TaskResult(TaskResultStatus.INFO, msg2)

        msg_multi = 'multi message'
        status_multi = TaskResultStatus.FAILURE
        multi = MultiTaskResult(status_multi, msg_multi, [result1, result2])

        self.assertEqual(
            self.serializer.dumps(multi), f'{{"status": "FAILURE", "message": "{msg_multi}", "results": [' +
            f'{{"status": "SUCCESS", "message": "{msg1}"}}, {{"status": "INFO", "message": "{msg2}"}}]}}')

    def test_unsupported_type_result_in_exception(self):

        class UnsupportedClass(object):
            pass

        with self.assertRaises(TypeError):
            self.serializer.dumps(UnsupportedClass())
