import mock
from pathlib import PurePath
import os
import asynctest
from checklisting.result import TaskResult
from checklisting.result.status import TaskResultStatus
from checklisting.tasks.subprocess import SubprocessTask, BaseSubprocessResultValidator


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