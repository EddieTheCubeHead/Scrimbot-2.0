__version__ = "0.1"
__author__ = "Eetu Asikainen"

from contextlib import contextmanager
from threading import Lock

from hintedi import HinteDI


class _RemovedDependencySentinel:
    pass


_lock = Lock()


@contextmanager
def mock_dependency(mocked_class, mock):
    original_dependency = HinteDI.dependencies.pop(mocked_class, _RemovedDependencySentinel())
    HinteDI.dependencies[mocked_class] = mock
    with _lock:
        try:
            yield
        finally:
            if not isinstance(original_dependency, _RemovedDependencySentinel):
                HinteDI.dependencies[mocked_class] = original_dependency
            else:
                HinteDI.dependencies.pop(mocked_class)
