__version__ = "0.1"
__author__ = "Eetu Asikainen"

from collections import OrderedDict

from Utils.TestBases.UnittestBase import UnittestBase

from Bot.Core.BotCache import BotCache
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestBotCache(UnittestBase):

    @BotCache
    def cached_function(self, arg: str):
        self.cached_function_call_count += 1
        return f"-{arg}-"

    @BotCache.with_maxsize(2)
    def small_cache_function(self, arg: int):
        self.small_cache_calls.append(arg)
        return f"={arg}="

    @cached_function.reset
    def reset_function(self, arg: str):
        return f"+{arg}+"

    @cached_function.update
    def update_function(self, arg: str):
        return f"*{arg}*"

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()

    def setUp(self) -> None:
        self.cached_function_call_count: int = 0
        self.small_cache_calls: list[int] = []

    def test_decorator_when_decorated_function_called_then_functionality_intact(self):
        unique_id = self.id_generator.generate_viable_id()
        self.assertEqual(f"-Test{unique_id}-", self.cached_function(f"Test{unique_id}"))

    def test_decorator_when_decorated_function_called_twice_then_cache_utilized(self):
        unique_id = self.id_generator.generate_viable_id()
        self.assertEqual(f"-Test{unique_id}-", self.cached_function(f"Test{unique_id}"))
        self.assertEqual(f"-Test{unique_id}-", self.cached_function(f"Test{unique_id}"))
        self.assertEqual(1, self.cached_function_call_count)

    def test_reset_when_decorated_function_called_with_value_then_cached_function_call_with_value_reset(self):
        unique_id = self.id_generator.generate_viable_id()
        self.assertEqual(f"-Test{unique_id}-", self.cached_function(f"Test{unique_id}"))
        self.assertEqual(f"+Test{unique_id}+", self.reset_function(f"Test{unique_id}"))
        self.assertEqual(f"-Test{unique_id}-", self.cached_function(f"Test{unique_id}"))
        self.assertEqual(2, self.cached_function_call_count)

    def test_update_when_decorated_function_called_with_value_then_cached_function_call_with_value_updated(self):
        unique_id = self.id_generator.generate_viable_id()
        self.assertEqual(f"-Test{unique_id}-", self.cached_function(f"Test{unique_id}"))
        self.update_function(f"Test{unique_id}")
        self.assertEqual(f"*Test{unique_id}*", self.cached_function(f"Test{unique_id}"))
        self.assertEqual(1, self.cached_function_call_count)

    def test_decorator_when_maxsize_reached_then_least_recent_calls_removed(self):
        self._call_small_cache_function_with(1, 2, 1, 3, 1, 4, 4, 1, 3)
        self.assertEqual([1, 2, 3, 4, 3], self.small_cache_calls)

    def _call_small_cache_function_with(self, *calls: int):
        for call in calls:
            self.small_cache_function(call)
