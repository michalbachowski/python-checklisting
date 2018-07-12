from enum import Enum


class TaskResultStatus(Enum):
    FAILURE = 50
    WARNING = 40
    SUCCESS = 30
    INFO = 20
    UNKNOWN = 10

    def __str__(self):
        return self.name
