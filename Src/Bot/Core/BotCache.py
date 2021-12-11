__version__ = "0.1"
__author__ = "Eetu Asikainen"

from collections import OrderedDict, Callable
from types import MethodType


class BotCache:

    def __init__(self, func):
        self.cache: OrderedDict = OrderedDict()
        self._func: Callable = func
        self._maxsize = 512

    @classmethod
    def with_maxsize(cls, maxsize: int):
        def maxsize_wrapper(func):
            instance = cls(func)
            instance._maxsize = maxsize
            return instance
        return maxsize_wrapper

    def __get__(self, instance, object_type):
        if instance is None:
            return self
        return MethodType(self, instance)

    def __call__(self, instance, *args, **kwargs):
        if (*args, *kwargs) in self.cache:
            return self._get_from_cache(*args, **kwargs)
        result = self._func(instance, *args, **kwargs)
        self._update_cache((*args, *kwargs), result)
        return result

    def reset(self, func):
        def wrapper(instance, *args, **kwargs):
            if (*args, *kwargs) in self.cache:
                self._remove_from_cache(*args, **kwargs)
            return func(instance, *args, **kwargs)
        return wrapper

    def update(self, func):
        def wrapper(instance, *args, **kwargs):
            result = func(instance, *args, **kwargs)
            if (*args, *kwargs) in self.cache:
                self._update_cache((*args, *kwargs), result)
            return result
        return wrapper

    def _get_from_cache(self, *args, **kwargs):
        self.cache.move_to_end((*args, *kwargs))
        return self.cache[(*args, *kwargs)]

    def _remove_from_cache(self, *args, **kwargs):
        self.cache.pop((*args, *kwargs))

    def _update_cache(self, key, result):
        self.cache[key] = result
        if len(self.cache) > self._maxsize:
            self.cache.popitem(last=False)
