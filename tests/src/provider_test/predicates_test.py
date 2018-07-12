import unittest

from checklisting.task import Checklist
from checklisting.provider.predicates import (AllowAllChecklistsFilterPredicate, WhitelistChecklistFilterPredicate)


class AllowAllChecklistsFilterPredicateTest(unittest.TestCase):

    def test_always_return_true(self):
        predicate = AllowAllChecklistsFilterPredicate()
        inputs = ['', None, Checklist('test', [])]
        for arg in inputs:
            self.assertTrue(predicate(arg))


class WhitelistChecklistFilterPredicateTest(unittest.TestCase):

    def test_requires_one_arg(self):
        with self.assertRaises(TypeError):
            WhitelistChecklistFilterPredicate()

    def test_requires_container(self):
        predicate = WhitelistChecklistFilterPredicate(None)
        with self.assertRaises(TypeError):
            predicate(Checklist('foo', []))

    def test_requires_checklist(self):
        predicate = WhitelistChecklistFilterPredicate(['foo'])
        with self.assertRaises(AttributeError):
            predicate(None)
        with self.assertRaises(AttributeError):
            predicate('')

    def test_allows_only_checklists_from_whitelist(self):
        checklist_ok = Checklist('foo', [])
        checklist_error = Checklist('bar', [])
        whitelist = [checklist_ok.name]
        predicate = WhitelistChecklistFilterPredicate(whitelist)
        self.assertTrue(predicate(checklist_ok))
        self.assertFalse(predicate(checklist_error))
