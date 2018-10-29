import asyncio
import os
from typing import Iterable, Iterator, NamedTuple, Optional

from checklisting.extras import import_module
from checklisting.result import BaseTaskResult, MultiTaskResult, TaskResult
from checklisting.result.builder import MultiTaskResultBuilder
from checklisting.result.status import TaskResultStatus
from checklisting.task import BaseTask

psutil = import_module('psutil')

GIGABYTE = 1024**3

DiskInfoStruct = NamedTuple('DiskInfoStruct', [('mountpoint', str), ('device', str), ('fstype', str), ('total', int),
                                               ('used', int), ('percent', float)])
CPUUsageStruct = NamedTuple('CPUUsageStruct', [('user', float), ('system', float), ('idle', float), ('iowait', float)])


async def _cpu_times_percent(interval: float) -> Iterable[CPUUsageStruct]:
    psutil.cpu_times_percent(interval=None, percpu=True)
    await asyncio.sleep(interval)
    cpu_times = psutil.cpu_times_percent(interval=None, percpu=True)
    assert isinstance(cpu_times, Iterable)  # always True since percpu=True; just making mypy happy
    return map(lambda scpu: CPUUsageStruct(scpu.user, scpu.system, scpu.idle, scpu.iowait), cpu_times)


class CPULoadValidator(object):

    def __init__(self, per_cpu_load_warn_treshold: float = 1.5, per_cpu_load_error_treshold: float = 2.0) -> None:
        assert per_cpu_load_error_treshold > per_cpu_load_warn_treshold
        assert per_cpu_load_warn_treshold > 0
        self._per_cpu_load_warn_treshold = per_cpu_load_warn_treshold
        self._per_cpu_load_error_treshold = per_cpu_load_error_treshold

    def validate(self, logical_cpu_count: int, cpu_load_1_minute: float, cpu_load_5_minute: float,
                 cpu_load_15_minute: float) -> BaseTaskResult:
        total_load_warn_treshold = logical_cpu_count * self._per_cpu_load_warn_treshold
        total_load_error_treshold = logical_cpu_count * self._per_cpu_load_error_treshold
        msg = f'System load 1m is [{cpu_load_1_minute}] which is'
        if cpu_load_1_minute > total_load_error_treshold:
            return TaskResult(TaskResultStatus.FAILURE,
                              f'{msg} greater than error treshold [{total_load_error_treshold}/CPU]')
        if cpu_load_1_minute > total_load_warn_treshold:
            return TaskResult(TaskResultStatus.WARNING,
                              f'{msg} greater than warning treshold [{total_load_warn_treshold}/CPU]')
        return TaskResult(TaskResultStatus.SUCCESS, f'{msg} at acceptable level')


class CPUCountValidator(object):

    def validate(self, physical_cpu_count: int, logical_cpu_count: int) -> BaseTaskResult:
        return TaskResult(TaskResultStatus.INFO,
                          f'Number of CPU: logical=[{logical_cpu_count}], physical=[{physical_cpu_count}]')


class CPUUsageValidator(object):

    def __init__(self, result_builder: Optional[MultiTaskResultBuilder] = None) -> None:
        self._result_builder = result_builder or MultiTaskResultBuilder()

    def _validate_cpu_usage_info(self, interval: float,
                                 cpu_usage_list: Iterator[CPUUsageStruct]) -> Iterator[BaseTaskResult]:
        for (idx, cpu_usage_info) in enumerate(cpu_usage_list):
            yield TaskResult(
                TaskResultStatus.INFO, f'CPU times for CPU #{idx} for past [{interval}] seconds are: ' +
                f'user=[{cpu_usage_info.user}]; system=[{cpu_usage_info.system}]; ' +
                f'idle=[{cpu_usage_info.idle}]; iowait=[{cpu_usage_info.iowait}]')

    def validate(self, interval: float, cpu_usage_list: Iterator[CPUUsageStruct]) -> MultiTaskResult:
        return self._result_builder.of_results(self._validate_cpu_usage_info(interval, cpu_usage_list))


class CPUInfoValidator(object):

    def __init__(self,
                 cpu_load_validator: Optional[CPULoadValidator] = None,
                 cpu_usage_validator: Optional[CPUUsageValidator] = None,
                 cpu_count_validator: Optional[CPUCountValidator] = None,
                 result_builder: Optional[MultiTaskResultBuilder] = None) -> None:
        self._result_builder = result_builder or MultiTaskResultBuilder()
        self._cpu_load_validator = cpu_load_validator or CPULoadValidator()
        self._cpu_usage_validator = cpu_usage_validator or CPUUsageValidator()
        self._cpu_count_validator = cpu_count_validator or CPUCountValidator()

    def validate(self, interval: float, cpu_usage_list: Iterator[CPUUsageStruct], cpu_load_1_minute: float,
                 cpu_load_5_minute: float, cpu_load_15_minute: float, physical_cpu_count: int,
                 logical_cpu_count: int) -> BaseTaskResult:
        return self._result_builder.of_results([
            self._cpu_load_validator.validate(logical_cpu_count, cpu_load_1_minute, cpu_load_5_minute,
                                              cpu_load_15_minute),
            self._cpu_count_validator.validate(physical_cpu_count, logical_cpu_count),
            self._cpu_usage_validator.validate(interval, cpu_usage_list)
        ])


class CPUInfoTask(BaseTask):

    def __init__(self, interval: float = 5.0, cpu_info_validator: Optional[CPUInfoValidator] = None) -> None:
        super().__init__()
        self._interval = interval
        self._cpu_info_validator = cpu_info_validator or CPUInfoValidator()

    async def _execute(self) -> BaseTaskResult:
        cpu_usage_list_task = asyncio.create_task(_cpu_times_percent(self._interval))

        try:
            logical_cpu_count = psutil.cpu_count(logical=True)
            if logical_cpu_count is None:
                print('fpoo')
                raise RuntimeError('Could not determine number of logical CPUs')

            physical_cpu_count = psutil.cpu_count(logical=False)
            if physical_cpu_count is None:
                raise RuntimeError('Could not determine number of physical CPUs')
        except Exception:
            cpu_usage_list_task.cancel()
            try:
                await cpu_usage_list_task
            except asyncio.CancelledError:
                pass
            raise
        else:
            cpu_usage_list = await cpu_usage_list_task

        (cpu_load_1_minute, cpu_load_5_minute, cpu_load_15_minute) = os.getloadavg()

        return self._cpu_info_validator.validate(self._interval, cpu_usage_list, cpu_load_1_minute, cpu_load_5_minute,
                                                 cpu_load_15_minute, physical_cpu_count, logical_cpu_count)


class MemoryInfoValidator(object):

    def __init__(self, usage_percent_warn_treshold: float = 80, usage_percent_error_treshold: float = 95) -> None:
        assert usage_percent_error_treshold > usage_percent_warn_treshold
        assert usage_percent_warn_treshold > 0
        self._usage_percent_error_treshold = usage_percent_error_treshold
        self._usage_percent_warn_treshold = usage_percent_warn_treshold

    def validate(self, mem_total: int, mem_used_percent: float) -> BaseTaskResult:
        gigs = round(mem_total / GIGABYTE, 2)

        msg = f'System memory is [{gigs}] GB is used in [{mem_used_percent}%] which is'
        if mem_used_percent > self._usage_percent_error_treshold:
            return TaskResult(TaskResultStatus.FAILURE,
                              f'{msg} greater than error treshold [{self._usage_percent_error_treshold}%]')
        if mem_used_percent > self._usage_percent_warn_treshold:
            return TaskResult(TaskResultStatus.WARNING,
                              f'{msg} greater than warning treshold [{self._usage_percent_warn_treshold}%]')
        return TaskResult(TaskResultStatus.SUCCESS, f'{msg} at acceptable level')


class MemoryInfoTask(BaseTask):

    def __init__(self, memory_info_validator: Optional[MemoryInfoValidator] = None) -> None:
        super().__init__()
        self._validator = memory_info_validator or MemoryInfoValidator()

    async def _execute(self) -> BaseTaskResult:
        mem = psutil.virtual_memory()
        return self._validator.validate(mem.total, mem.percent)


class DiskInfoValidator(object):

    def __init__(self,
                 usage_percent_warn_treshold: float = 80,
                 usage_percent_error_treshold: float = 95,
                 result_builder: Optional[MultiTaskResultBuilder] = None) -> None:
        assert usage_percent_error_treshold > usage_percent_warn_treshold
        assert usage_percent_warn_treshold > 0
        self._usage_percent_warn_treshold = usage_percent_warn_treshold
        self._usage_percent_error_treshold = usage_percent_error_treshold
        self._result_builder = result_builder or MultiTaskResultBuilder()

    def _validate_disk_info_struct(self, disk_info_struct: DiskInfoStruct) -> BaseTaskResult:
        total_gigs = round(disk_info_struct.total / GIGABYTE, 2)

        msg = f'Device [{disk_info_struct.device}] (mount: [{disk_info_struct.mountpoint}]; ' +\
            f'fstype: [{disk_info_struct.fstype}]) has [{total_gigs}] GB in total and is used in ' +\
            f'[{disk_info_struct.percent}%] which is'
        if disk_info_struct.percent > self._usage_percent_error_treshold:
            return TaskResult(TaskResultStatus.FAILURE,
                              f'{msg} greater than error treshold [{self._usage_percent_error_treshold}%]')
        if disk_info_struct.percent > self._usage_percent_warn_treshold:
            return TaskResult(TaskResultStatus.WARNING,
                              f'{msg} greater than warning treshold [{self._usage_percent_warn_treshold}%]')
        return TaskResult(TaskResultStatus.SUCCESS, f'{msg} at acceptable level')

    def _build_results(self, disk_info_list: Iterator[DiskInfoStruct]) -> Iterator[BaseTaskResult]:
        for disk_info_struct in disk_info_list:
            yield self._validate_disk_info_struct(disk_info_struct)

    def validate(self, disk_info_list: Iterable[DiskInfoStruct]) -> MultiTaskResult:
        return self._result_builder.of_results(self._build_results(iter(disk_info_list)))


class DiskInfoTask(BaseTask):

    def __init__(self, disk_info_validator: Optional[DiskInfoValidator] = None) -> None:
        super().__init__()
        self._disk_info_validator = disk_info_validator or DiskInfoValidator()

    async def _execute(self) -> BaseTaskResult:
        partitions = psutil.disk_partitions()
        disk_info_structs = []
        for partition in partitions:
            usage = psutil.disk_usage(partition.mountpoint)
            disk_info_structs.append(
                DiskInfoStruct(partition.mountpoint, partition.device, partition.fstype, usage.total, usage.used,
                               usage.percent))
        return self._disk_info_validator.validate(disk_info_structs)
