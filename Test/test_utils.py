__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import Tuple, Type, Optional

from Src.Database.DatabaseManager import DatabaseManager
from Src.Database.DatabaseConnectionWrapper import DatabaseConnectionWrapper


def assert_tuple_with_correct_types(actual: Tuple, *tuple_fields: Type) -> Optional[str]:
    if len(actual) != len(tuple_fields):
        return f"Expected a tuple with length of {len(tuple_fields)}, actual length was {len(actual)}!"
    for actual, expected in zip(actual, tuple_fields):
        if not isinstance(actual, expected):
            return f"Expected an instance of {expected}, got an instance of {type(actual)}."


class DisposableManagerWrapper:

    def __init__(self, manager: DatabaseManager):
        self._manager = manager
