import os
from pathlib import PurePath

import asynctest
import mock

from checklisting.result import BaseTaskResult, TaskResult
from checklisting.result.status import TaskResultStatus
from checklisting.tasks.subprocess import BaseSubprocessResultValidator, SubprocessTask


class ExceptionRaisingValidator(BaseSubprocessResultValidator):

    def _validate(self, stdout: str, stderr: str, exit_code: int) -> BaseTaskResult:
        raise RuntimeError("test")


class SubprocessTaskTest(asynctest.TestCase):

    def setUp(self):
        self.process_path = str(PurePath(os.environ['FIXTURES_DIR']) / 'process.py')
        self.validator = mock.Mock(BaseSubprocessResultValidator)
        self.validator.validate.return_value = TaskResult(TaskResultStatus.SUCCESS, 'mock_output')

    async def test_on_subprocess_exit_calls_validator(self):
        task = SubprocessTask([self.process_path], self.validator)

        result = await task.execute()

        self.assertEqual(result.status, TaskResultStatus.SUCCESS)
        self.assertEqual(result.message, 'mock_output')
        self.validator.validate.assert_called_once_with(b'', b'', 0)

    async def test_passes_stdout_stderr_and_exitcode_to_validator(self):
        task = SubprocessTask([self.process_path, '--stdout', 'out', '--stderr', 'err', '--exit', "42"],
                              self.validator)

        result = await task.execute()

        self.assertEqual(result.status, TaskResultStatus.SUCCESS)
        self.assertEqual(result.message, 'mock_output')
        self.validator.validate.assert_called_once_with(b'out', b'err', 42)

    async def test_on_validation_error_returns_failure(self):
        task = SubprocessTask([self.process_path], ExceptionRaisingValidator())

        result = await task.execute()
        self.assertEqual(result.status, TaskResultStatus.UNKNOWN)
        self.assertTrue(result.message.endswith("Exception:\ntest"))
