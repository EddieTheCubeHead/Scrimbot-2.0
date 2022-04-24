__version__ = "0.1"
__author__ = "Eetu Asikainen"

from abc import ABC
from typing import TypeVar, Generic

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.DataClasses.DataClass import DataClass
from Database.Core.MasterConnection import MasterConnection

T = TypeVar('T', bound=DataClass)  # pylint: disable=invalid-name


class ConnectionBase(ABC, Generic[T]):  # pylint: disable=too-few-public-methods

    @BotDependencyInjector.inject
    def __init__(self, master_connection: MasterConnection):
        self._master_connection = master_connection
