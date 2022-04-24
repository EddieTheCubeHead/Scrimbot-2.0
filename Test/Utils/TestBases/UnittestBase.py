__version__ = "0.1"
__author__ = "Eetu Asikainen"


import unittest
from typing import Callable

from Bot.Core.BotDependencyInjector import BotDependencyInjector, InstanceSentinel


class UnittestBase(unittest.TestCase):

    def _assert_raises_correct_exception(self, excepted_exception: Exception, call: Callable, *args, **kwargs):
        with self.assertRaises(type(excepted_exception)) as context:
            call(*args, **kwargs)

        self.assertEqual(str(excepted_exception), str(context.exception))
        return context.exception

    def _assert_singleton_dependency(self, dependency_class: type):
        dependency_type = BotDependencyInjector.dependencies[dependency_class]
        if dependency_type:
            self.assertIsInstance(dependency_type, dependency_class)

    def _assert_instance_dependency(self, dependency_class: type):
        self.assertIsInstance(BotDependencyInjector.dependencies[dependency_class], InstanceSentinel)
