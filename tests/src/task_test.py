import mock
import asynctest
from checklisting.task import BaseTask, MultiTask, Checklist
from checklisting.result import TaskResult
from checklisting.result.builder import MultiTaskResultBuilder
from checklisting.result.status import TaskResultStatus


class BaseTaskTest(asynctest.TestCase):

    def setUp(self):

        class TestTask(BaseTask):

            async def _execute(self):
                raise RuntimeError("foo")

        self.task = TestTask()

    async def test_exceptions_are_transformed_to_failures(self):
        result = await self.task.execute()
        self.assertEqual(result.status, TaskResultStatus.FAILURE)
        self.assertEqual(result.message, "foo")


class MultiTaskTest(asynctest.TestCase):

    def setUp(self):
        self._result1 = mock.Mock(TaskResult)
        self._result1.status = TaskResultStatus.INFO
        self._task1 = asynctest.mock.Mock(BaseTask)
        self._task1.execute.return_value = self._result1
        self._result2 = mock.Mock(TaskResult)
        self._result2.status = TaskResultStatus.SUCCESS
        self._task2 = asynctest.mock.Mock(BaseTask)
        self._task2.execute.return_value = self._result2
        self._result_builder = mock.Mock(MultiTaskResultBuilder)
        self._multi_task = MultiTask([self._task1, self._task2], self._result_builder)

    async def test_exceptions_are_transformed_to_failures(self):
        self._task1.execute.side_effect = RuntimeError("foo")
        result = await self._multi_task.execute()
        self.assertEqual(result.status, TaskResultStatus.FAILURE)
        self.assertEqual(result.message, "foo")

    async def test_inner_tasks_are_executed_and_responses_are_collected(self):
        await self._multi_task.execute()
        self._result_builder.of_results.assert_called_once_with([self._result1, self._result2])

    async def test_defaults(self):
        multi_task = MultiTask([self._task1, self._task2])
        result = await multi_task.execute()
        self.assertEqual(result.status, TaskResultStatus.SUCCESS)
        self.assertEqual(result.message, 'Task success.')


class ChecklistTest(asynctest.TestCase):

    def setUp(self):
        self._name = 'test_checklist'
        self._result1 = mock.Mock(TaskResult)
        self._result1.status = TaskResultStatus.INFO
        self._result1.message = 'msg1'
        self._task1 = asynctest.mock.Mock(BaseTask)
        self._task1.execute.return_value = self._result1
        self._result2 = mock.Mock(TaskResult)
        self._result2.status = TaskResultStatus.SUCCESS
        self._result2.message = 'msg2'
        self._task2 = asynctest.mock.Mock(BaseTask)
        self._task2.execute.return_value = self._result2
        self._result_builder = mock.Mock(MultiTaskResultBuilder)
        self._checklist = Checklist(self._name, [self._task1, self._task2], self._result_builder)

    async def test_exceptions_are_transformed_to_failures(self):
        self._task1.execute.side_effect = RuntimeError("foo")
        result = await self._checklist.execute()
        self.assertEqual(result.status, TaskResultStatus.FAILURE)
        self.assertEqual(result.message, "foo")

    async def test_inner_tasks_are_executed_and_responses_are_collected(self):
        await self._checklist.execute()
        self._result_builder.of_results.assert_called_once_with([self._result1, self._result2])

    async def test_defaults(self):
        _checklist = Checklist(self._name, [self._task1, self._task2])
        result = await _checklist.execute()
        self.assertEqual(result.status, TaskResultStatus.SUCCESS)
        self.assertEqual(result.message, 'Checklist [test_checklist]: Task success.')

    def test_get_name(self):
        self.assertEqual(self._checklist.name, self._name)
