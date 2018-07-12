import mock
from pathlib import Path
import asynctest
from checklisting.result.status import TaskResultStatus
from checklisting.tasks.path import FileExistsTask, DirectoryExistsTask


class FileExistsTaskTest(asynctest.TestCase):

    def setUp(self):
        self.path = mock.MagicMock(Path)
        self.path.__str__.return_value = 'test_path'
        self.path.is_file.return_value = False
        self.path.is_dir.return_value = False
        self.task = FileExistsTask(self.path)

    def test_no_path_given_raises_error(self):
        with self.assertRaises(TypeError):
            FileExistsTask()

    async def test_None_path_given_returns_failure(self):
        task = FileExistsTask(None)
        result = await task.execute()

        self.assertEqual(result.status, TaskResultStatus.FAILURE)
        self.assertEqual(result.message, "'NoneType' object has no attribute 'is_file'")

    async def test_when_file_does_not_exist_failure_is_returned(self):
        result = await self.task.execute()

        self.assertEqual(result.status, TaskResultStatus.FAILURE)
        self.assertEqual(result.message, "File [test_path] does NOT exist")

    async def test_when_file_is_a_directory_warning_is_returned(self):
        self.path.is_dir.return_value = True
        result = await self.task.execute()

        self.assertEqual(result.status, TaskResultStatus.WARNING)
        self.assertEqual(result.message, "Path [test_path] is a directory, not a file")

    async def test_when_file_exists_success_is_returned(self):
        self.path.is_file.return_value = True
        result = await self.task.execute()

        self.assertEqual(result.status, TaskResultStatus.SUCCESS)
        self.assertEqual(result.message, "File [test_path] exists")

    def test_str_returns_path(self):
        self.assertEqual(str(self.task), 'test_path')

    def test_eq_compares_two_paths(self):
        self.assertEqual(FileExistsTask(Path('/')), FileExistsTask(Path('/')))


class DirectoryExistsTaskTest(asynctest.TestCase):

    def setUp(self):
        self.path = mock.MagicMock(Path)
        self.path.__str__.return_value = 'test_dir'
        self.path.is_file.return_value = False
        self.path.is_dir.return_value = False
        self.task = DirectoryExistsTask(self.path)

    def test_no_path_given_raises_error(self):
        with self.assertRaises(TypeError):
            DirectoryExistsTask()

    async def test_None_path_given_returns_failure(self):
        task = DirectoryExistsTask(None)
        result = await task.execute()

        self.assertEqual(result.status, TaskResultStatus.FAILURE)
        self.assertEqual(result.message, "'NoneType' object has no attribute 'is_dir'")

    async def test_when_directory_does_not_exist_failure_is_returned(self):
        result = await self.task.execute()

        self.assertEqual(result.status, TaskResultStatus.FAILURE)
        self.assertEqual(result.message, "Directory [test_dir] does NOT exist")

    async def test_when_directory_is_a_file_warning_is_returned(self):
        self.path.is_file.return_value = True
        result = await self.task.execute()

        self.assertEqual(result.status, TaskResultStatus.WARNING)
        self.assertEqual(result.message, "Path [test_dir] is a file, not a directory")

    async def test_when_directory_exists_success_is_returned(self):
        self.path.is_dir.return_value = True
        result = await self.task.execute()

        self.assertEqual(result.status, TaskResultStatus.SUCCESS)
        self.assertEqual(result.message, "Directory [test_dir] exists")

    def test_str_returns_path(self):
        self.assertEqual(str(self.task), 'test_dir')

    def test_eq_compares_two_paths(self):
        self.assertEqual(DirectoryExistsTask(Path('/')), DirectoryExistsTask(Path('/')))
