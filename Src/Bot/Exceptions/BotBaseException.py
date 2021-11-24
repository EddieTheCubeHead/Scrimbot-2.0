__version__ = "0.1"
__author__ = "Eetu Asikainen"

from abc import ABC, abstractmethod

from discord.ext import commands


class BotBaseException(commands.CommandError, ABC):

    @abstractmethod
    def resolve(self):
        pass
