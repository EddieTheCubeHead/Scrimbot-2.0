__version__ = "0.1"
__author__ = "Eetu Asikainen"

from contextlib import contextmanager
from threading import Lock

from Bot.Core.BotDependencyInjector import BotDependencyInjector


class _RemovedDependencySentinel:
    pass


_lock = Lock()


@contextmanager
def mock_dependency(mocked_class, mock):
    original_dependency = BotDependencyInjector.dependencies.pop(mocked_class, _RemovedDependencySentinel())
    BotDependencyInjector.dependencies[mocked_class] = mock
    with _lock:
        try:
            yield
        finally:
            if not isinstance(original_dependency, _RemovedDependencySentinel):
                BotDependencyInjector.dependencies[mocked_class] = original_dependency
            else:
                BotDependencyInjector.dependencies.pop(mocked_class)
