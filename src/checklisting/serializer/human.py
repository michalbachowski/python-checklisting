from typing import Iterator

from checklisting.serializer import BaseSerializer
from checklisting.result import BaseTaskResult, MultiTaskResult


class HumanReadableSerializer(BaseSerializer):

    INDENT_LENGTH = 4

    def dumps(self, result: BaseTaskResult) -> str:
        return '\n'.join(self._dumps(result, 0))

    def get_lines(self, result: BaseTaskResult) -> Iterator[str]:
        yield from self._dumps(result, 0)

    def _dumps(self, result: BaseTaskResult, indent_level: int) -> Iterator[str]:
        yield self._msg(result, indent_level)

        if isinstance(result, MultiTaskResult):
            for inner_result in result.results:
                yield from self._dumps(inner_result, indent_level + 1)

    def _msg(self, result: BaseTaskResult, indent_level: int) -> str:
        indentation = ' ' * HumanReadableSerializer.INDENT_LENGTH * indent_level
        return f'{indentation}[{result.status:<8}] {result.message}'
