__version__ = "0.1"
__author__ = "Eetu Asikainen"

import threading
from typing import List


class TestIdGenerator:

    def __init__(self, valid_start: int = 0, invalid_start: int = 0):
        self.generated: set = set()
        self._viable_iterator = valid_start
        self._nonviable_iterator = invalid_start
        self._viable_generator = self._generate_viable()
        self._nonviable_generator = self._generate_nonviable()
        self._generator_lock: threading.Lock = threading.Lock()

    def generate_viable_id_group(self, group_length=1) -> List[int]:
        return [self.generate_viable_id() for _ in range(group_length)]

    def generate_viable_id(self) -> int:
        return next(self._viable_generator)

    def generate_nonviable_id_group(self, group_length=1) -> List[int]:
        return [self.generate_nonviable_id() for _ in range(group_length)]

    def generate_nonviable_id(self) -> int:
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


GLOBAL_ID_GENERATOR = TestIdGenerator(100)
