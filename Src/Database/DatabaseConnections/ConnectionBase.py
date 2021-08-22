__version__ = "0.1"
__author__ = "Eetu Asikainen"

from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from Bot.Converters.Convertable import Convertable

T = TypeVar('T', bound=Convertable)


class ConnectionBase(ABC, Generic[T]):

    def __init__(self, connection_string: str):
        self._connection_string = connection_string

    @abstractmethod
    def get_from_id(self, object_id: int) -> T:  # pragma: no cover
        pass

    @abstractmethod
    def get_multiple(self, *object_ids: int) -> list[T]:
        pass

    @abstractmethod
    def get_all(self) -> list[T]:
        pass

    @abstractmethod
    def insert(self, new_object: T):
        pass

    @abstractmethod
    def update(self, updated_object: T):
        pass
