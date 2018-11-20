import unittest
from typing import Any, Iterable, Mapping, Union

from checklisting.result import BaseTaskResult, MultiTaskResult, TaskResult
from checklisting.result.status import TaskResultStatus
from checklisting.serializer.json import JsonDeserializer, JsonSerializer, task_result_decoder


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


class JsonDeserializerTest(unittest.TestCase):

    def setUp(self) -> None:
        self.serializer = JsonSerializer()
        self.deserializer = JsonDeserializer()

    def _do_test(self, results: BaseTaskResult) -> None:
        result_string = self.serializer.dumps(results)

        deserialized_result = self.deserializer.loads(result_string)

        self.assertEqual(deserialized_result, results)

    def test_valid_json_result_test(self) -> None:
        self._do_test(TaskResult(TaskResultStatus.INFO, "test message"))

    def test_valid_json_simple_multi_result_test(self) -> None:
        self._do_test(
            MultiTaskResult(TaskResultStatus.FAILURE, "failure message", [
                TaskResult(TaskResultStatus.INFO, "test message"),
            ]))

    def test_valid_json_nested_multi_result_test(self) -> None:
        self._do_test(
            MultiTaskResult(TaskResultStatus.FAILURE, "failure message", [
                TaskResult(TaskResultStatus.INFO, "test message"),
                MultiTaskResult(TaskResultStatus.SUCCESS, "success message", [
                    TaskResult(TaskResultStatus.WARNING, "warning message"),
                    MultiTaskResult(TaskResultStatus.UNKNOWN, "unknown message", [
                        TaskResult(TaskResultStatus.FAILURE, "failure 2 message")
                    ])
                ])
            ]))

    def test_missing_message(self) -> None:
        input_dict = dict(a=1, status='FAILURE')
        serialized = self.serializer.dumps(input_dict)
        deserialized = self.deserializer.loads(serialized)

        self.assertDictEqual(input_dict, deserialized)

    def test_missing_status(self) -> None:
        input_dict = dict(a=1, message='FAILURE')
        serialized = self.serializer.dumps(input_dict)
        deserialized = self.deserializer.loads(serialized)

        self.assertDictEqual(input_dict, deserialized)

    def test_missing_all_but_results(self) -> None:
        input_dict = dict(a=1, results='foo')
        serialized = self.serializer.dumps(input_dict)
        deserialized = self.deserializer.loads(serialized)

        self.assertDictEqual(input_dict, deserialized)

    def test_valid_task_result_with_non_iterable_results_returns_TaskResult(self) -> None:
        input_results = TaskResult(TaskResultStatus.FAILURE, 'test message')
        input_dict = dict(status=input_results.status, message=input_results.message, results=1)
        serialized = self.serializer.dumps(input_dict)
        deserialized = self.deserializer.loads(serialized)

        self.assertEqual(input_results, deserialized)
