__version__ = "0.1"
__author__ = "Eetu Asikainen"

from abc import ABC, abstractmethod


class ConnectionBase(ABC):

    def __init__(self, connection_string: str):
        self._connection_string = connection_string

    @abstractmethod
    def get_from_id(self, object_id: int):  # pragma: no cover
        pass
