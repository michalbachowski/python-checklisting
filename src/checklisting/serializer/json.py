import json

from checklisting.result import BaseTaskResult, MultiTaskResult
from checklisting.result.status import TaskResultStatus
from . import BaseSerializer


def task_result_encoder(obj):
    if isinstance(obj, TaskResultStatus):
        return str(obj)
    if isinstance(obj, BaseTaskResult):
        output = dict(status=obj.status, message=obj.message)
        if isinstance(obj, MultiTaskResult):
            output['results'] = obj.results
        return output
    raise TypeError(f"Cannot JSON-encode obj {type(obj)}")


class JsonSerializer(BaseSerializer):

    def dumps(self, result: BaseTaskResult) -> str:
        return json.dumps(result, default=task_result_encoder)
