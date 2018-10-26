import types
import unittest

import mock

from checklisting.extras import has_module, import_module, list_extra_modules


class ExtrasTest(unittest.TestCase):

    def test_has_module_returns_true_for_extra_modules(self):
        self.assertTrue(has_module('aiohttp'))
        self.assertTrue(has_module('psutil'))

    def test_has_module_returns_false_for_non_extra_module(self):
        self.assertFalse(has_module('non_extra_module'))

    def test_import_module_returns_module_if_this_is_extra_module(self):
        for module_name in list_extra_modules():
            module = import_module(module_name)
            self.assertIsInstance(module, types.ModuleType)
            self.assertEqual(module.__name__, module_name)

    def test_import_module_raises_exception_if_this_is_non_extra_module(self):
        with self.assertRaises(RuntimeError):
            try:
                import_module('non_extra_module')
            except RuntimeError as e:
                self.assertEqual(
                    str(e),
                    'Module [non_extra_module] is not part of any extras, ' + 'please use standard import statement')
                raise

    def test_import_module_raises_exception_if_extra_module_is_missing(self):
        with self.assertRaises(RuntimeError), mock.patch('checklisting.extras.has_module', return_value=False):
            try:
                import_module('aiohttp')
            except RuntimeError as e:
                self.assertEqual(
                    str(e), 'Please install [web] extras to use [aiohttp] ' +
                    f'(required by [{__name__}]): pip install checklisting[web]')
                raise
