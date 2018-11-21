import json
from typing import Iterable

from checklisting.result import BaseTaskResult, MultiTaskResult, TaskResult
from checklisting.result.status import TaskResultStatus

from . import BaseDeserializer, BaseSerializer


def task_result_encoder(obj):
    if isinstance(obj, TaskResultStatus):
        return str(obj)
    if isinstance(obj, BaseTaskResult):
        output = dict(status=obj.status, message=obj.message)
        if isinstance(obj, MultiTaskResult):
            output['results'] = obj.results
        return output
    raise TypeError(f"Cannot JSON-encode obj {type(obj)}")


def task_result_decoder(obj):
    if 'status' in obj and 'message' in obj:
        status = TaskResultStatus[obj['status']]
        message = obj['message']

        if 'results' in obj and isinstance(obj['results'], Iterable):
            return MultiTaskResult(status, message, obj['results'])
        else:
            return TaskResult(status, message)
    return obj


class JsonSerializer(BaseSerializer):

    def dumps(self, result: BaseTaskResult) -> str:
        return json.dumps(result, default=task_result_encoder)


class JsonDeserializer(BaseDeserializer):

    def loads(self, result: str) -> BaseTaskResult:
        return json.loads(result, object_hook=task_result_decoder)
