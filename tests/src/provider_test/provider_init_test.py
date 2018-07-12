import unittest

import mock

from checklisting.task import Checklist
from checklisting.provider import StaticChecklistsProvider


class StaticChecklistsProviderTest(unittest.TestCase):

    def setUp(self):
        self._checklists = [
            mock.Mock(Checklist),
            mock.Mock(Checklist),
        ]
        self._provider = StaticChecklistsProvider(self._checklists)

    def test_returns_given_checklists_as_is(self):
        checklists = self._provider.get_all()

        self.assertCountEqual(checklists, self._checklists)

    def test_returns_iterator(self):
        checklists = self._provider.get_all()

        list(checklists)
        self.assertCountEqual(checklists, [])

    def test_will_exhaust_iterator_if_given(self):
        gen = (c for c in self._checklists)
        provider = StaticChecklistsProvider(gen)

        self.assertCountEqual(gen, [])
        self.assertCountEqual(provider.get_all(), self._checklists)
        self.assertCountEqual(provider.get_all(), self._checklists)

    def test_returns_new_iterator_each_time(self):
        checklists = self._provider.get_all()

        self.assertIsNot(checklists, self._provider.get_all())

    def test_returns_checklists_matching_predicate(self):
        predicate = mock.Mock(side_effect=[True, False])
        self.assertCountEqual(self._provider.get_filtered(predicate), [self._checklists[0]])
        predicate.assert_has_calls(list(map(mock.call, self._checklists)))
