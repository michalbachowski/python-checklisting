import unittest
from checklisting.result import TaskResult
from checklisting.result.status import TaskResultStatus
from checklisting.result.message.builder import BaseTaskResultMessageBuilder, \
                                                    StatusAwareTaskResultMessageBuilder, PrefixedTaskResultMessageBuilder


class StatusAwareTaskResultMessageBuilderTest(unittest.TestCase):

    def setUp(self):
        self.builder = StatusAwareTaskResultMessageBuilder()

    def test_only_status_is_taken_into_account(self):
        msg = 'test_message'
        message = self.builder.build(TaskResultStatus.INFO, [msg])
        self.assertNotIn(msg, message)

    def test_all_statuses(self):
        expected = {
            TaskResultStatus.FAILURE: 'Task failure. See subtasks for details.',
            TaskResultStatus.WARNING: 'Task error. See subtasks for details.',
            TaskResultStatus.SUCCESS: 'Task success.',
            TaskResultStatus.INFO: 'Task completed. See subtasks for details.',
            TaskResultStatus.UNKNOWN: 'Task is in unknown state. See subtasks for details.',
        }
        msg = 'test_message'

        for status in TaskResultStatus:
            self.assertEqual(
                self.builder.build(status, [msg]), expected[status], f'Incorrect message for status=[{status}]')

    def test_build_and_of_results_creates_same_results(self):
        msg = 'test_message'

        for status in TaskResultStatus:
            result = TaskResult(status, msg)
            self.assertEqual(
                self.builder.build(status, msg), self.builder.of_results(status, [result]),
                f'Incorrect message for status=[{status}]')


class PrefixedTaskResultMessageBuilderTest(unittest.TestCase):

    def setUp(self):
        self.prefix = 'test_prefix'
        self.inner_builder = unittest.mock.Mock(BaseTaskResultMessageBuilder)
        self.inner_builder.build.return_value = 'mocked_message'
        self.builder = PrefixedTaskResultMessageBuilder(self.prefix, self.inner_builder)

    def test_prefixes_all_messages_with_given_prefix(self):
        msg = 'test_message'
        self.assertEqual(self.builder.build(TaskResultStatus.INFO, [msg]), f'{self.prefix}mocked_message')
        self.inner_builder.build.assert_called_once_with(TaskResultStatus.INFO, [msg])
        self.assertEqual(self.inner_builder.of_results.call_count, 0)

    def test_calls_onlt_build_on_inner_builder_not_of_results(self):
        msg = 'test_message'
        result = TaskResult(TaskResultStatus.UNKNOWN, msg)
        self.assertEqual(self.builder.of_results(TaskResultStatus.INFO, [result]), f'{self.prefix}mocked_message')
        self.inner_builder.build.assert_called_once_with(TaskResultStatus.INFO, [msg])
        self.assertEqual(self.inner_builder.of_results.call_count, 0)

    def test_defaults(self):
        msg = 'test_message'
        builder = PrefixedTaskResultMessageBuilder(self.prefix)
        self.assertEqual(
            builder.build(TaskResultStatus.INFO, [msg]), f'{self.prefix}Task completed. See subtasks for details.')
