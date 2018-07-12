import random
import unittest

import mock

from checklisting.result.status import TaskResultStatus
from checklisting.result.status.validator import (AggregatedTaskResultStatusValidator,
                                                  AllOfSameTypeTaskResultStatusValidator,
                                                  AvailableStatusTaskResultStatusValidator,
                                                  BaseTaskResultStatusValidator,
                                                  DefaultTaskResultStatusValidator,
                                                  FallbackTaskResultStatusValidator,
                                                  MostCommonTaskResultStatusValidator,
                                                  PrioritizedTaskResultStatusValidator)


class FallbackTaskResultStatusValidatorTest(unittest.TestCase):

    def setUp(self):
        self.inner_validator = mock.MagicMock(BaseTaskResultStatusValidator)
        self.fallback = mock.MagicMock(return_value="foo")
        self.validator = FallbackTaskResultStatusValidator(self.fallback, self.inner_validator)

    def test_call_fallback_when_UNKNOWN_status_from_inner_validator(self):
        self.inner_validator.validate.return_value = TaskResultStatus.UNKNOWN
        result = self.validator.validate(None)

        self.inner_validator.validate.assert_called_once_with(None)
        self.fallback.assert_called_once_with()
        self.assertEqual(result, "foo")

    def test_skip_fallback_when_status_from_inner_validator_differ_from_UNKNOWN(self):
        self.inner_validator.validate.return_value = TaskResultStatus.INFO
        result = self.validator.validate(None)

        self.inner_validator.validate.assert_called_once_with(None)
        self.assertEqual(self.fallback.call_count, 0)
        self.assertEqual(result, TaskResultStatus.INFO)

    def test_None_input_is_handled_by_inner_validator(self):
        self.inner_validator.validate.return_value = TaskResultStatus.UNKNOWN
        result = self.validator.validate(None)

        self.inner_validator.validate.assert_called_once_with(None)
        self.fallback.assert_called_once_with()
        self.assertEqual(result, "foo")

    def test_empty_list_of_results_is_handled_by_inner_validator(self):
        self.inner_validator.validate.return_value = TaskResultStatus.UNKNOWN
        result = self.validator.validate([])

        self.inner_validator.validate.assert_called_once_with([])
        self.fallback.assert_called_once_with()
        self.assertEqual(result, "foo")


class AllOfSameTypeTaskResultStatusValidatorTest(unittest.TestCase):

    def setUp(self):
        self.validator = AllOfSameTypeTaskResultStatusValidator()

    def test_None_input(self):
        result = self.validator.validate(None)
        self.assertEqual(result, TaskResultStatus.UNKNOWN)

    def test_empty_list_of_results(self):
        result = self.validator.validate([])
        self.assertEqual(result, TaskResultStatus.UNKNOWN)

    def test_one_result(self):
        for status in TaskResultStatus:
            result = self.validator.validate([status])
            self.assertEqual(result, status)

    def test_all_same_results(self):
        for status in TaskResultStatus:
            result = self.validator.validate([status] * 3)
            self.assertEqual(result, status)

    def test_multiple_different_results(self):
        result = self.validator.validate([TaskResultStatus.SUCCESS, TaskResultStatus.FAILURE, TaskResultStatus.INFO])
        self.assertEqual(result, TaskResultStatus.UNKNOWN)


class MostCommonTaskResultStatusValidatorTask(unittest.TestCase):

    def setUp(self):
        self.validator = MostCommonTaskResultStatusValidator()

    def test_None_input(self):
        result = self.validator.validate(None)
        self.assertEqual(result, TaskResultStatus.UNKNOWN)

    def test_empty_list_of_results(self):
        result = self.validator.validate([])
        self.assertEqual(result, TaskResultStatus.UNKNOWN)

    def test_one_result(self):
        for status in TaskResultStatus:
            result = self.validator.validate([status])
            self.assertEqual(result, status)

    def test_all_same_results(self):
        for status in TaskResultStatus:
            result = self.validator.validate([status] * 3)
            self.assertEqual(result, status)

    def test_multiple_different_results(self):
        result = self.validator.validate(
            [TaskResultStatus.SUCCESS, TaskResultStatus.FAILURE, TaskResultStatus.INFO, TaskResultStatus.SUCCESS])
        self.assertEqual(result, TaskResultStatus.SUCCESS)

    def test_multiple_statuses_with_same_number_of_occurences(self):
        result = self.validator.validate([TaskResultStatus.SUCCESS, TaskResultStatus.FAILURE, TaskResultStatus.INFO])
        self.assertEqual(result, TaskResultStatus.UNKNOWN)


class AvailableStatusTaskResultStatusValidatorTest(unittest.TestCase):

    def setUp(self):
        self.validator = AvailableStatusTaskResultStatusValidator(TaskResultStatus.INFO)

    def test_None_input(self):
        result = self.validator.validate(None)
        self.assertEqual(result, TaskResultStatus.UNKNOWN)

    def test_empty_list_of_results(self):
        result = self.validator.validate([])
        self.assertEqual(result, TaskResultStatus.UNKNOWN)

    def test_one_valid_result(self):
        result = self.validator.validate([TaskResultStatus.INFO])
        self.assertEqual(result, TaskResultStatus.INFO)

    def test_one_invalid_result(self):
        result = self.validator.validate([TaskResultStatus.SUCCESS])
        self.assertEqual(result, TaskResultStatus.UNKNOWN)

    def test_multiple_results_with_valid_one(self):
        result = self.validator.validate(
            [TaskResultStatus.INFO, TaskResultStatus.FAILURE, TaskResultStatus.INFO, TaskResultStatus.SUCCESS])
        self.assertEqual(result, TaskResultStatus.INFO)

    def test_multiple_results_without_valid_one(self):
        result = self.validator.validate([TaskResultStatus.SUCCESS, TaskResultStatus.FAILURE])
        self.assertEqual(result, TaskResultStatus.UNKNOWN)


class AggregatedTaskResultStatusValidatorTest(unittest.TestCase):

    def setUp(self):
        self.validator1 = mock.MagicMock(BaseTaskResultStatusValidator)
        self.validator2 = mock.MagicMock(BaseTaskResultStatusValidator)
        self.validator = AggregatedTaskResultStatusValidator(self.validator1, self.validator2)

    def test_stop_validation_at_first_result_different_than_UNKNOWN(self):
        self.validator1.validate.return_value = TaskResultStatus.UNKNOWN
        self.validator2.validate.return_value = TaskResultStatus.UNKNOWN
        result = self.validator.validate(None)

        self.validator1.validate.assert_called_once_with(None)
        self.validator2.validate.assert_called_once_with(None)
        self.assertEqual(result, TaskResultStatus.UNKNOWN)

    def test_stop_validation_at_first_result_different_than_UNKNOWN_1(self):
        self.validator1.validate.return_value = TaskResultStatus.UNKNOWN
        self.validator2.validate.return_value = TaskResultStatus.INFO
        result = self.validator.validate(None)

        self.validator1.validate.assert_called_once_with(None)
        self.validator2.validate.assert_called_once_with(None)
        self.assertEqual(result, TaskResultStatus.INFO)

    def test_stop_validation_at_first_result_different_than_UNKNOWN_2(self):
        self.validator1.validate.return_value = TaskResultStatus.SUCCESS
        self.validator2.validate.return_value = TaskResultStatus.INFO
        result = self.validator.validate(None)

        self.validator1.validate.assert_called_once_with(None)
        self.assertEqual(self.validator2.call_count, 0)
        self.assertEqual(result, TaskResultStatus.SUCCESS)

    def test_None_input_is_handled_by_inner_validators(self):
        self.validator1.validate.return_value = TaskResultStatus.UNKNOWN
        self.validator2.validate.return_value = TaskResultStatus.UNKNOWN
        result = self.validator.validate(None)

        self.validator1.validate.assert_called_once_with(None)
        self.validator2.validate.assert_called_once_with(None)
        self.assertEqual(result, TaskResultStatus.UNKNOWN)

    def test_None_input_is_handled_by_inner_validators_1(self):
        self.validator1.validate.return_value = TaskResultStatus.UNKNOWN
        self.validator2.validate.return_value = TaskResultStatus.INFO
        result = self.validator.validate(None)

        self.validator1.validate.assert_called_once_with(None)
        self.validator2.validate.assert_called_once_with(None)
        self.assertEqual(result, TaskResultStatus.INFO)

    def test_empty_list_of_results_is_handled_by_inner_validators(self):
        self.validator1.validate.return_value = TaskResultStatus.UNKNOWN
        self.validator2.validate.return_value = TaskResultStatus.INFO
        result = self.validator.validate([])

        self.validator1.validate.assert_called_once_with([])
        self.validator2.validate.assert_called_once_with([])
        self.assertEqual(result, TaskResultStatus.INFO)

    def test_empty_list_of_results_is_handled_by_inner_validators_1(self):
        self.validator1.validate.return_value = TaskResultStatus.UNKNOWN
        self.validator2.validate.return_value = TaskResultStatus.UNKNOWN
        result = self.validator.validate([])

        self.validator1.validate.assert_called_once_with([])
        self.validator2.validate.assert_called_once_with([])
        self.assertEqual(result, TaskResultStatus.UNKNOWN)


class PrioritizedTaskResultStatusValidatorTest(unittest.TestCase):

    def setUp(self):
        self.validator = PrioritizedTaskResultStatusValidator()

    def test_FAILURE_has_top_priority(self):
        statuses = [
            TaskResultStatus.FAILURE, TaskResultStatus.WARNING, TaskResultStatus.SUCCESS, TaskResultStatus.INFO,
            TaskResultStatus.UNKNOWN
        ]
        random.shuffle(statuses)
        result = self.validator.validate(statuses)
        self.assertEqual(result, TaskResultStatus.FAILURE)

    def test_WARNING_has_second_to_top_priority(self):
        statuses = [
            TaskResultStatus.WARNING, TaskResultStatus.SUCCESS, TaskResultStatus.INFO, TaskResultStatus.UNKNOWN
        ]
        random.shuffle(statuses)
        result = self.validator.validate(statuses)
        self.assertEqual(result, TaskResultStatus.WARNING)

    def test_SUCCESS_has_third_to_top_priority(self):
        statuses = [TaskResultStatus.SUCCESS, TaskResultStatus.INFO, TaskResultStatus.UNKNOWN]
        random.shuffle(statuses)
        result = self.validator.validate(statuses)
        self.assertEqual(result, TaskResultStatus.SUCCESS)

    def test_INFO_has_second_lowest_priority(self):
        statuses = [TaskResultStatus.INFO, TaskResultStatus.UNKNOWN]
        random.shuffle(statuses)
        result = self.validator.validate(statuses)
        self.assertEqual(result, TaskResultStatus.INFO)

    def test_UNKNOWN_has_the_lowest_priority(self):
        statuses = [TaskResultStatus.UNKNOWN]
        random.shuffle(statuses)
        result = self.validator.validate(statuses)
        self.assertEqual(result, TaskResultStatus.UNKNOWN)

    def test_None_input(self):
        result = self.validator.validate(None)
        self.assertEqual(result, TaskResultStatus.UNKNOWN)

    def test_empty_list(self):
        statuses = []
        random.shuffle(statuses)
        result = self.validator.validate(statuses)
        self.assertEqual(result, TaskResultStatus.UNKNOWN)


class DefaultTaskResultStatusValidatorTest(unittest.TestCase):

    def setUp(self):
        self.validator = DefaultTaskResultStatusValidator()

    def test_None_input(self):
        result = self.validator.validate(None)
        self.assertEqual(result, TaskResultStatus.UNKNOWN)

    def test_empty_list_of_results(self):
        result = self.validator.validate([])
        self.assertEqual(result, TaskResultStatus.UNKNOWN)

    def test_one_result(self):
        for status in TaskResultStatus:
            result = self.validator.validate([status])
            self.assertEqual(result, status)

    def test_all_same_results(self):
        for status in TaskResultStatus:
            result = self.validator.validate([status] * 3)
            self.assertEqual(result, status)

    def test_for_multiple_different_results_FAILURE_has_top_priority(self):
        statuses = [
            TaskResultStatus.FAILURE, TaskResultStatus.WARNING, TaskResultStatus.SUCCESS, TaskResultStatus.INFO,
            TaskResultStatus.UNKNOWN
        ]
        random.shuffle(statuses)
        result = self.validator.validate(statuses)
        self.assertEqual(result, TaskResultStatus.FAILURE)

    def test_for_multiple_different_results_WARNING_has_second_to_top_priority(self):
        statuses = [
            TaskResultStatus.WARNING, TaskResultStatus.SUCCESS, TaskResultStatus.INFO, TaskResultStatus.UNKNOWN
        ]
        random.shuffle(statuses)
        result = self.validator.validate(statuses)
        self.assertEqual(result, TaskResultStatus.WARNING)

    def test_for_multiple_different_results_SUCCESS_has_third_to_top_priority(self):
        statuses = [TaskResultStatus.SUCCESS, TaskResultStatus.INFO, TaskResultStatus.UNKNOWN]
        random.shuffle(statuses)
        result = self.validator.validate(statuses)
        self.assertEqual(result, TaskResultStatus.SUCCESS)

    def test_for_multiple_different_results_INFO_has_second_lowest_priority(self):
        statuses = [TaskResultStatus.INFO, TaskResultStatus.UNKNOWN]
        random.shuffle(statuses)
        result = self.validator.validate(statuses)
        self.assertEqual(result, TaskResultStatus.INFO)

    def test_UNKNOWN_has_the_lowest_priority(self):
        statuses = [TaskResultStatus.UNKNOWN]
        random.shuffle(statuses)
        result = self.validator.validate(statuses)
        self.assertEqual(result, TaskResultStatus.UNKNOWN)
