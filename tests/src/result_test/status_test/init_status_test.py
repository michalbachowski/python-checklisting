import unittest
from checklisting.result.status import TaskResultStatus


class TaskResultStatusTest(unittest.TestCase):

    def test_str_returns_expected_values(self):
        expected = {
            TaskResultStatus.UNKNOWN: 'UNKNOWN',
            TaskResultStatus.INFO: 'INFO',
            TaskResultStatus.SUCCESS: 'SUCCESS',
            TaskResultStatus.WARNING: 'WARNING',
            TaskResultStatus.FAILURE: 'FAILURE',
        }
        for status in TaskResultStatus:
            self.assertEqual(expected[status], str(status))
