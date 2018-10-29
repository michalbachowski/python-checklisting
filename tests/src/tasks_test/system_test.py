import unittest
from typing import Iterable, Iterator
from unittest import mock

import asynctest

from checklisting.result import BaseTaskResult, TaskResult
from checklisting.result.builder import MultiTaskResultBuilder
from checklisting.result.status import TaskResultStatus
from checklisting.tasks.system import (CPUCountValidator, CPUInfoTask, CPUInfoValidator, CPULoadValidator,
                                       CPUUsageStruct, CPUUsageValidator, DiskInfoStruct, DiskInfoTask,
                                       DiskInfoValidator, MemoryInfoTask, MemoryInfoValidator)
from checklisting.testing import CheckGenerator, CheckType


class CPUCountValidatorTest(unittest.TestCase):

    def test_returns_task_result_instance(self):  # type: ignore
        self.assertIsInstance(CPUCountValidator().validate(1, 2), BaseTaskResult)

    def test_returned_task_is_of_info_type(self):  # type: ignore
        self.assertEqual(CPUCountValidator().validate(1, 2).status, TaskResultStatus.INFO)


class CPULoadValidatorTest(unittest.TestCase):

    def setUp(self):  # type: ignore
        self.warn_treshold = 10.0
        self.error_treshold = 100.0
        self.validator = CPULoadValidator(self.warn_treshold, self.error_treshold)

    def test_raises_exception_when_error_treshold_less_than_warn(self):  # type: ignore
        with self.assertRaises(AssertionError):
            CPULoadValidator(2.0, 1.0)

    def test_raises_exception_when_warn_treshold_less_than_zero(self):  # type: ignore
        with self.assertRaises(AssertionError):
            CPULoadValidator(-1.0, 2.0)

    def test_validate_returns_instance_of_BaseTaskResult(self):  # type: ignore
        self.assertIsInstance(self.validator.validate(4, 1.0, 1.0, 1.0), BaseTaskResult)

    def test_validate_return_message_contains_information_about_1m_load_only(self):  # type: ignore
        load_1m = 1.0
        load_5m = 2.0
        load_15m = 3.0
        logical_cpu_count = 4
        ret = self.validator.validate(logical_cpu_count, load_1m, load_5m, load_15m)
        self.assertIn(str(load_1m), ret.message)
        self.assertNotIn(str(load_5m), ret.message)
        self.assertNotIn(str(load_15m), ret.message)

    def test_validate_return_status_depends_on_load_1m_only(self):  # type: ignore
        ret = self.validator.validate(4, 0.1, 200.0, 0.1)
        self.assertIs(ret.status, TaskResultStatus.SUCCESS)

        ret = self.validator.validate(4, 0.1, 0.1, 200.0)
        self.assertIs(ret.status, TaskResultStatus.SUCCESS)

        ret = self.validator.validate(4, 200.0, 0.1, 0.1)
        self.assertIsNot(ret.status, TaskResultStatus.SUCCESS)

    def test_validate_returns_WARNING_when_load_1m_is_between_warn_treshold_and_error_treshold(self):  # type: ignore
        logical_cpu_count = 4
        load_1m = 20.0
        ret = self.validator.validate(logical_cpu_count, logical_cpu_count * load_1m, 0.1, 0.1)
        self.assertIs(ret.status, TaskResultStatus.WARNING)

    def test_validate_returns_ERROR_when_load_1m_is_above_error_treshold(self):  # type: ignore
        logical_cpu_count = 4
        load_1m = 200.0
        ret = self.validator.validate(logical_cpu_count, logical_cpu_count * load_1m, 0.1, 0.1)
        self.assertIs(ret.status, TaskResultStatus.FAILURE)


class CPUUsageValidatorTest(unittest.TestCase):

    def setUp(self):  # type: ignore
        self.validator = CPUUsageValidator()
        self.usage1 = CPUUsageStruct(1.0, 2.0, 3.0, 4.0)
        self.usage2 = CPUUsageStruct(5.0, 6.0, 7.0, 8.0)
        self.usages = [self.usage1, self.usage2]
        self.interval = 9.0

    def test_validate_returns_instance_of_BaseTaskResult(self):  # type: ignore
        self.assertIsInstance(self.validator.validate(self.interval, iter(self.usages)), BaseTaskResult)

    def test_validate_returns_only_INFO_results(self):  # type: ignore
        result = self.validator.validate(self.interval, self.usages)

        self.assertIs(result.status, TaskResultStatus.INFO)

        for inner_result in result.results:
            self.assertIs(inner_result.status, TaskResultStatus.INFO)

    def test_validate_returns_usage_information(self):  # type: ignore
        result = self.validator.validate(self.interval, self.usages)

        for (idx, inner_result) in enumerate(result.results):
            self.assertIn(str(self.interval), inner_result.message)
            self.assertIn(str(idx), inner_result.message)
            for member in self.usages[idx]._fields:
                self.assertIn(member, inner_result.message)
                self.assertIn(str(getattr(self.usages[idx], member)), inner_result.message)


class CPUInfoValidatorTest(unittest.TestCase):

    def setUp(self):  # type: ignore
        self.load_result = mock.Mock(BaseTaskResult)
        self.load_validator = mock.Mock(CPULoadValidator)
        self.load_validator.validate = mock.Mock(return_value=self.load_result)
        self.usage_result = mock.Mock(BaseTaskResult)
        self.usage_validator = mock.Mock(CPUUsageValidator)
        self.usage_validator.validate = mock.Mock(return_value=self.usage_result)
        self.count_result = mock.Mock(BaseTaskResult)
        self.count_validator = mock.Mock(CPUCountValidator)
        self.count_validator.validate = mock.Mock(return_value=self.count_result)
        self.builder_result = mock.Mock(BaseTaskResult)
        self.result_builder = mock.Mock(MultiTaskResultBuilder)
        self.result_builder.of_results.return_value = self.builder_result
        self.validator = CPUInfoValidator(self.load_validator, self.usage_validator, self.count_validator,
                                          self.result_builder)

    def test_validate_calls_inner_validators_and_returns_result_from_result_builder(self):  # type: ignore
        interval = 1.0
        cpu_usage_list: Iterator[CPUUsageStruct] = iter(list())
        cpu_load_1_minute = 2.0
        cpu_load_5_minute = 3.0
        cpu_load_15_minute = 4.0
        physical_cpu_count = 5
        logical_cpu_count = 10
        expected_results = [self.load_result, self.count_result, self.usage_result]

        result = self.validator.validate(interval, cpu_usage_list, cpu_load_1_minute, cpu_load_5_minute,
                                         cpu_load_15_minute, physical_cpu_count, logical_cpu_count)
        self.assertIs(result, self.builder_result)
        self.result_builder.of_results.assert_called_once_with(CheckGenerator(expected_results))
        self.load_validator.validate.assert_called_once_with(logical_cpu_count, cpu_load_1_minute, cpu_load_5_minute,
                                                             cpu_load_15_minute)
        self.usage_validator.validate.assert_called_once_with(interval, cpu_usage_list)
        self.count_validator.validate.assert_called_once_with(physical_cpu_count, logical_cpu_count)


class CPUInfoTaskTest(asynctest.TestCase):

    def setUp(self):  # type: ignore
        self.interval = 1.0
        self.result = mock.Mock(BaseTaskResult)
        self.validator = mock.Mock(CPUInfoValidator())
        self.validator.validate.return_value = self.result
        self.task = CPUInfoTask(self.interval, self.validator)

    async def test_returns_error_when_could_not_load_logical_cpu_count(self):  # type: ignore
        with mock.patch('checklisting.tasks.system.psutil.cpu_count', return_value=None):
            result = await CPUInfoTask().execute()
            self.assertEqual(result.status, TaskResultStatus.FAILURE)

    async def test_returns_error_when_could_not_load_physical_cpu_count(self):  # type: ignore
        with mock.patch('checklisting.tasks.system.psutil.cpu_count', side_effect=[1, None]) as cpu_count:
            result = await CPUInfoTask(self.interval).execute()
            self.assertEqual(result.status, TaskResultStatus.FAILURE)
            cpu_count.assert_has_calls([mock.call(logical=True), mock.call(logical=False)])

    async def test_properly_calls_validator(self):  # type: ignore
        result = await self.task.execute()
        self.assertIs(result, self.result)
        self.validator.validate.assert_called_once_with(self.interval, CheckType(Iterable), CheckType(float),
                                                        CheckType(float), CheckType(float), CheckType(int),
                                                        CheckType(int))

    async def test_cpu_usage_list_is_cancelled_if_cpu_count_cannot_be_obtained(self):  # type: ignore
        with asynctest.patch('checklisting.tasks.system._cpu_times_percent'),\
             mock.patch('checklisting.tasks.system.psutil.cpu_count', side_effect=[1, None]):
            result = await CPUInfoTask(self.interval).execute()
            self.assertEqual(result.status, TaskResultStatus.FAILURE)


class MemoryInfoValidatorTest(asynctest.TestCase):

    def setUp(self):  # type: ignore
        self._warn = 85
        self._error = 90
        self._mem_total = 1024**3 * 8
        self.validator = MemoryInfoValidator(self._warn, self._error)

    def test_returns_error_when_memory_usage_above_error_treshold(self):  # type: ignore
        result = self.validator.validate(self._mem_total, self._error + 1)
        self.assertEqual(result.status, TaskResultStatus.FAILURE)
        self.assertEqual(result.message,
                         'System memory is [8.0] GB is used in [91%] which is greater than error treshold [90%]')

    def test_returns_success_when_memory_usage_below_warn_treshold(self):  # type: ignore
        result = self.validator.validate(self._mem_total, self._warn - 1)
        self.assertEqual(result.status, TaskResultStatus.SUCCESS)
        self.assertEqual(result.message, 'System memory is [8.0] GB is used in [84%] which is at acceptable level')

    def test_returns_warning_when_memory_usage_between_warn_and_error_treshold(self):  # type: ignore
        result = self.validator.validate(self._mem_total, self._warn + 1)
        self.assertEqual(result.status, TaskResultStatus.WARNING)
        self.assertEqual(result.message,
                         'System memory is [8.0] GB is used in [86%] which is greater than warning treshold [85%]')


class MemoryInfoTaskTest(asynctest.TestCase):

    def setUp(self):  # type: ignore
        self._validator = mock.Mock(MemoryInfoValidator)
        self._task = MemoryInfoTask(self._validator)

    async def test_execute_calls_predefined_validator(self):  # type: ignore
        await self._task.execute()
        self._validator.validate.assert_called_once_with(mock.ANY, mock.ANY)


class DiskInfoValidatorTest(unittest.TestCase):

    def setUp(self):  # type: ignore
        self._warn = 85
        self._error = 90
        self._validator = DiskInfoValidator(self._warn, self._error)
        self._disk_provider = lambda usage: DiskInfoStruct('/test', 'test0', 'testfs', 1000, 10, usage)

    def test_validator_calls_provided_builder(self):
        builder_result = mock.Mock(BaseTaskResult)
        result_builder = mock.Mock(MultiTaskResultBuilder)
        result_builder.of_results.return_value = builder_result
        validator = DiskInfoValidator(self._warn, self._error, result_builder)

        result = validator.validate([self._disk_provider(0)])

        self.assertIs(result, builder_result)
        expected_results = [
            TaskResult(
                TaskResultStatus.SUCCESS, 'Device [test0] (mount: [/test]; fstype: [testfs]) has [0.0] GB in total ' +
                'and is used in [0%] which is at acceptable level')
        ]
        result_builder.of_results.assert_called_once_with(CheckGenerator(expected_results))

    def test_returns_error_when_disk_usage_above_error_treshold(self):  # type: ignore
        disk = self._disk_provider(self._error + 1)
        result = self._validator.validate([disk])

        self.assertEqual(result.status, TaskResultStatus.FAILURE)
        self.assertEqual(len(result.results), 1)

        inner_result = result.results.pop()

        self.assertEqual(inner_result.status, TaskResultStatus.FAILURE)
        self.assertEqual(
            inner_result.message,
            'Device [test0] (mount: [/test]; fstype: [testfs]) has [0.0] GB in total ' +
            'and is used in [91%] which is greater than error treshold [90%]'
        )

    def test_returns_success_when_disk_usage_below_warn_treshold(self):  # type: ignore
        disk = self._disk_provider(self._warn - 1)
        result = self._validator.validate([disk])

        self.assertEqual(result.status, TaskResultStatus.SUCCESS)
        self.assertEqual(len(result.results), 1)

        inner_result = result.results.pop()

        self.assertEqual(inner_result.status, TaskResultStatus.SUCCESS)
        self.assertEqual(
            inner_result.message,
            'Device [test0] (mount: [/test]; fstype: [testfs]) has [0.0] GB in total ' +
            'and is used in [84%] which is at acceptable level'
        )

    def test_returns_warning_when_disk_usage_between_warn_and_error_treshold(self):  # type: ignore
        disk = self._disk_provider(self._warn + 1)
        result = self._validator.validate([disk])

        self.assertEqual(result.status, TaskResultStatus.WARNING)
        self.assertEqual(len(result.results), 1)

        inner_result = result.results.pop()

        self.assertEqual(inner_result.status, TaskResultStatus.WARNING)
        self.assertEqual(
            inner_result.message,
            'Device [test0] (mount: [/test]; fstype: [testfs]) has [0.0] GB in total ' +
            'and is used in [86%] which is greater than warning treshold [85%]'
        )


class DiskInfoTaskTest(asynctest.TestCase):

    def setUp(self):  # type: ignore
        self._validator = mock.Mock(DiskInfoValidator)
        self._task = DiskInfoTask(self._validator)

    async def test_execute_calls_predefined_validator(self):  # type: ignore
        await self._task.execute()
        self._validator.validate.assert_called_once_with(CheckType(Iterable))
