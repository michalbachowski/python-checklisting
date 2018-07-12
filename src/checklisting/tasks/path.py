from pathlib import Path
from checklisting.task import BaseTask
from checklisting.result import TaskResult
from checklisting.result.status import TaskResultStatus


class FileExistsTask(BaseTask):

    def __init__(self, path: Path) -> None:
        super().__init__()
        self._path = path

    async def _execute(self):
        if self._path.is_file():
            return TaskResult(TaskResultStatus.SUCCESS, f"File [{self._path}] exists")

        if self._path.is_dir():
            return TaskResult(TaskResultStatus.WARNING, f"Path [{self._path}] is a directory, not a file")

        return TaskResult(TaskResultStatus.FAILURE, f"File [{self._path}] does NOT exist")

    def __str__(self):
        return str(self._path)

    def __eq__(self, other):
        return str(self) == str(other)


class DirectoryExistsTask(BaseTask):

    def __init__(self, path: Path) -> None:
        self._path = path

    async def _execute(self):
        if self._path.is_dir():
            return TaskResult(TaskResultStatus.SUCCESS, f"Directory [{self._path}] exists")

        if self._path.is_file():
            return TaskResult(TaskResultStatus.WARNING, f"Path [{self._path}] is a file, not a directory")

        return TaskResult(TaskResultStatus.FAILURE, f"Directory [{self._path}] does NOT exist")

    def __str__(self):
        return str(self._path)

    def __eq__(self, other):
        return str(self) == str(other)
