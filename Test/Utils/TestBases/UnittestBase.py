__version__ = "0.1"
__author__ = "Eetu Asikainen"


import unittest
from typing import Callable, Hashable

from hintedi import HinteDI, InstanceSentinel


class UnittestBase(unittest.TestCase):

    def _assert_raises_correct_exception(self, excepted_exception: Exception, call: Callable, *args, **kwargs):
        with self.assertRaises(type(excepted_exception)) as context:
            call(*args, **kwargs)

        self.assertEqual(str(excepted_exception), str(context.exception))
        return context.exception

    def _assert_singleton_dependency(self, dependency_class: type):
        dependency_type = HinteDI.dependencies[dependency_class]
        if dependency_type:
            self.assertIsInstance(dependency_type, dependency_class)

    def _assert_instance_dependency(self, dependency_class: type):
        self.assertIsInstance(HinteDI.dependencies[dependency_class], InstanceSentinel)

    def _assert_abstract_base_dependency(self, dependency_class: type):
        self.assertEqual(dict, type(HinteDI.dependencies[dependency_class]))

    def _assert_singleton_concrete_dependency(self, dependency_class: type, base_class: type, key: Hashable):
        self._assert_singleton_dependency(dependency_class)
        self.assertEqual(dependency_class, HinteDI.dependencies[base_class][key])
