__version__ = "0.1"
__author__ = "Eetu Asikainen"

from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from sqlalchemy.orm import Query

from Bot.DataClasses.Convertable import Convertable
from Database.Core.MasterConnection import MasterConnection

T = TypeVar('T', bound=Convertable)


class ConnectionBase(ABC, Generic[T]):

    def __init__(self, master_connection: MasterConnection):
        self._master_connection = master_connection
