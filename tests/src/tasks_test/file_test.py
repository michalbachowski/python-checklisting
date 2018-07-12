import unittest
import mock
import pathlib
import asynctest
from checklisting.testing import CheckType, CheckGenerator
from checklisting.result import BaseTaskResult
from checklisting.result.builder import MultiTaskResultBuilder
from checklisting.result.status import TaskResultStatus
from checklisting.tasks.file import FileContentTask, BaseFileContentValidator, PerLineFileContentValidator, BaseLineValidator


class FileContentTaskTest(asynctest.TestCase):

    def setUp(self):
        self._path = mock.MagicMock(pathlib.Path)
        self._path.__str__.return_value = 'sample_path'
        self._path.exists.return_value = True
        self._result = mock.Mock(BaseTaskResult)
        self._validator = mock.Mock(BaseFileContentValidator)
        self._validator.validate.return_value = self._result
        self._task = FileContentTask(self._path, self._validator)

    def test_init_takes_2_args(self):
        with self.assertRaises(TypeError):
            FileContentTask()

        with self.assertRaises(TypeError):
            FileContentTask(None)

    async def test_when_file_does_not_exist_error_is_returned(self):
        self._path.exists.return_value = False
        result = await self._task.execute()

        self._path.exists.assert_called_once_with()
        self.assertEqual(result.status, TaskResultStatus.FAILURE)
        self.assertIn(str(self._path), result.message)

    async def test_when_file_exists_validator_is_called(self):
        data = 'line1\nline2'
        mock_open = mock.mock_open(read_data=data)
        with mock.patch('builtins.open', mock_open):
            result = await self._task.execute()

        self._path.exists.assert_called_once_with()
        mock_open.assert_called_once_with(self._path, 'r', 1)
        self.assertIs(result, self._result)


class PerLineFileContentValidatorTest(unittest.TestCase):

    def setUp(self):
        self._line_validator_result = mock.Mock(BaseTaskResult)
        self._line_validator = mock.Mock(BaseLineValidator)
        self._line_validator.validate.return_value = self._line_validator_result
        self._result = mock.Mock(BaseTaskResult)
        self._builder = mock.Mock(MultiTaskResultBuilder)
        self._builder.of_results.return_value = self._result
        self._validator = PerLineFileContentValidator(self._line_validator, self._builder)

    def test_init_requires_1_argument(self):
        with self.assertRaises(TypeError):
            PerLineFileContentValidator()

        PerLineFileContentValidator(None)

    def test_empty_lines_or_lines_containing_only_whitespace_are_skipped(self):
        self._builder.of_results.side_effect = list
        self._validator.validate(['', None, 0, '   ', '\t'])
        self.assertEqual(self._line_validator.validate.call_count, 0)

    def test_validation_is_lazy_evaluated_1(self):
        result = self._validator.validate(['bar', 'foo'])
        # this first to exhaust generator
        self._builder.of_results.assert_called_once_with(CheckType(filter))
        self.assertEqual(self._line_validator.validate.call_count, 0)
        self.assertIs(result, self._result)

    def test_validation_is_lazy_evaluated_2(self):
        self._builder.of_results.side_effect = next
        self._validator.validate(['bar', 'foo'])
        self._builder.of_results.assert_called_once_with(CheckType(filter))
        self.assertEqual(self._line_validator.validate.call_count, 1)

    def test_None_responses_from_inner_validator_are_skipped(self):
        self._line_validator.validate.side_effect = [None, self._result]
        self._validator.validate(['bar', 'foo'])
        # this first to exhaust generator
        self._builder.of_results.assert_called_once_with(CheckGenerator([self._result]))
        self.assertEqual(self._line_validator.validate.call_count, 2)

    def test_non_string_values_result_in_exception(self):
        self._builder.of_results.side_effect = list
        with self.assertRaises(TypeError):
            self._validator.validate([1])

    def test_non_empty_lines_are_validated(self):
        result = self._validator.validate(['', None, 0, 'foo'])
        # this first to exhaust generator
        self._builder.of_results.assert_called_once_with(CheckGenerator([self._line_validator_result]))
        self._line_validator.validate.assert_called_once_with('foo')
        self.assertIs(result, self._result)
