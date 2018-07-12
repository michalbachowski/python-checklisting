# encoding: utf-8
import mock
import unittest
from checklisting.result import TaskResult, MultiTaskResult
from checklisting.result.status import TaskResultStatus


class TaskResultTest(unittest.TestCase):

    def setUp(self):
        self.msg = "foo"
        self.status = TaskResultStatus.INFO
        self.result = TaskResult(self.status, self.msg)

    def test_status_getter(self):
        self.assertEqual(self.result.status, self.status)

    def test_message_getter(self):
        self.assertEqual(self.result.message, self.msg)

    def test_repr_displays_status_and_message(self):
        r = repr(self.result)

        self.assertIn(str(self.status), r)
        self.assertIn(self.msg, r)

    def test_repr_shortens_message(self):
        message = 'foobarbazbat'
        long_message = message * 5
        result = TaskResult(TaskResultStatus.INFO, long_message)
        r = repr(result)

        self.assertNotIn(long_message, r)
        self.assertIn(message, r)


class MultiTaskResultTest(unittest.TestCase):

    def setUp(self):
        self.result1 = mock.MagicMock()
        self.result1.status = TaskResultStatus.SUCCESS
        self.result1.message = "m1"
        self.result2 = mock.MagicMock()
        self.result2.status = TaskResultStatus.FAILURE
        self.result2.message = "m2"
        self.multi_result = MultiTaskResult(TaskResultStatus.INFO, "msg", [self.result1, self.result2])

    def test_status_is_given_explicite(self):
        result = self.multi_result.status

        self.assertEqual(result, TaskResultStatus.INFO)

    def test_message_is_given_explicite(self):
        result = self.multi_result.message

        self.assertEqual(result, "msg")

    def test_results_are_returned_as_is(self):
        self.assertEqual(self.multi_result.results, self.multi_result.results)
