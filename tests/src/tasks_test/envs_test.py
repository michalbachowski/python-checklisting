from random import randint
import asynctest
from checklisting.result.status import TaskResultStatus
from checklisting.tasks.envs import environ, CheckEnvironmentVariableTask


class CheckEnvironmentVariableTaskTest(asynctest.TestCase):

    def setUp(self):
        self._env_name = 'test_env{}'.format(randint(1, 1000))
        self._env_value = 'test_value'
        self.task = CheckEnvironmentVariableTask(self._env_name)

    def test_init_takes_one_argument(self):
        with self.assertRaises(TypeError):
            CheckEnvironmentVariableTask()

    async def test_when_env_is_missing_error_is_returned(self):
        result = await self.task.execute()
        self.assertEqual(result.status, TaskResultStatus.FAILURE)
        self.assertIn(self._env_name, result.message)

    async def test_when_env_exists_success_is_returned(self):
        environ[self._env_name] = self._env_value
        result = await self.task.execute()
        del environ[self._env_name]

        self.assertEqual(result.status, TaskResultStatus.SUCCESS)
        self.assertIn(self._env_name, result.message)
        self.assertIn(self._env_value, result.message)
