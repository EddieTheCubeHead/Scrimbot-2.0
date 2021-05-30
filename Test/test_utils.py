__version__ = "0.1"
__author__ = "Eetu Asikainen"

import threading
from typing import Tuple, Type, Optional


class UniqueIdGenerator:

    def __init__(self):
        self.generated: set = set()
        self._viable_iterator = 0
        self._nonviable_iterator = 0
        self._viable_generator = self._generate_viable()
        self._nonviable_generator = self._generate_nonviable()
        self._generator_lock: threading.Lock = threading.Lock()

    def generate_viable_id_group(self, group_length=1):
        return tuple([self.generate_viable_id() for _ in range(group_length)])

    def generate_viable_id(self):
        return next(self._viable_generator)

    def generate_nonviable_id_group(self, group_length=1):
        return tuple([self.generate_nonviable_id() for _ in range(group_length)])

    def generate_nonviable_id(self):
        return next(self._nonviable_generator)

    def _generate_viable(self):
        while True:
            with self._generator_lock:
                self._viable_iterator = self._generate_id(self._viable_iterator, 1)
            yield self._viable_iterator

    def _generate_nonviable(self):
        while True:
            with self._generator_lock:
                self._nonviable_iterator = self._generate_id(self._nonviable_iterator, -1)
            yield self._nonviable_iterator

    def _generate_id(self, base, iteration_step):
        base += iteration_step
        if base in self.generated:
            raise Exception("ID generator generated an already existing id!")
        self.generated.add(base)
        return base


def assert_tuple_with_correct_types(actual: Tuple, *tuple_fields: Type) -> Optional[str]:
    if len(actual) != len(tuple_fields):
        return f"Expected a tuple with length of {len(tuple_fields)}, actual length was {len(actual)}!"
    for actual, expected in zip(actual, tuple_fields):
        if not isinstance(actual, expected):
            return f"Expected an instance of {expected}, got an instance of {type(actual)}."
