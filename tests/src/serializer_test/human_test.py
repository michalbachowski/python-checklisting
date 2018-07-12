import unittest
from checklisting.result import TaskResult, MultiTaskResult
from checklisting.result.status import TaskResultStatus
from checklisting.serializer.human import HumanReadableSerializer


class HumanReadableSerializerTest(unittest.TestCase):

    def setUp(self):
        self.serializer = HumanReadableSerializer()

    def test_success_result(self):
        msg = 'success_message'
        result = TaskResult(TaskResultStatus.SUCCESS, msg)

        self.assertEqual(self.serializer.dumps(result), f'[SUCCESS ] {msg}')

    def test_failure_result(self):
        msg = 'failure_message'
        result = TaskResult(TaskResultStatus.FAILURE, msg)

        self.assertEqual(self.serializer.dumps(result), f'[FAILURE ] {msg}')

    def test_warning_result(self):
        msg = 'warning_message'
        result = TaskResult(TaskResultStatus.WARNING, msg)

        self.assertEqual(self.serializer.dumps(result), f'[WARNING ] {msg}')

    def test_info_result(self):
        msg = 'info_message'
        result = TaskResult(TaskResultStatus.INFO, msg)

        self.assertEqual(self.serializer.dumps(result), f'[INFO    ] {msg}')

    def test_unknown_result(self):
        msg = 'unknown_message'
        result = TaskResult(TaskResultStatus.UNKNOWN, msg)

        self.assertEqual(self.serializer.dumps(result), f'[UNKNOWN ] {msg}')

    def test_multi_result(self):
        msg1 = 'unknown_message'
        result1 = TaskResult(TaskResultStatus.SUCCESS, msg1)

        msg2 = 'unknown_message'
        result2 = TaskResult(TaskResultStatus.INFO, msg2)

        msg_multi = 'multi message'
        status_multi = TaskResultStatus.FAILURE
        multi = MultiTaskResult(status_multi, msg_multi, [result1, result2])

        self.assertCountEqual(
            list(self.serializer.get_lines(multi)), [
                f'[FAILURE ] {msg_multi}',
                f'    [SUCCESS ] {msg1}',
                f'    [INFO    ] {msg2}',
            ])

    def test_dumps_and_get_lines_produces_same_results(self):
        msg1 = 'message1'
        result1 = TaskResult(TaskResultStatus.SUCCESS, msg1)

        msg2 = 'message2'
        result2 = TaskResult(TaskResultStatus.INFO, msg2)

        msg_multi = 'multi message'
        status_multi = TaskResultStatus.FAILURE
        multi = MultiTaskResult(status_multi, msg_multi, [result1, result2])
        self.assertEqual(self.serializer.dumps(multi), '\n'.join(self.serializer.get_lines(multi)))

    def test_indentation(self):
        msg = 'unknown_message'
        result = TaskResult(TaskResultStatus.UNKNOWN, msg)

        self.assertEqual(self.serializer.dumps(result), f'[UNKNOWN ] {msg}')
