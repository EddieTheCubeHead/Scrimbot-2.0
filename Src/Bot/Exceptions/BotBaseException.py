__version__ = "0.1"
__author__ = "Eetu Asikainen"

from abc import ABC, abstractmethod

from discord.ext import commands
from discord.ext.commands import Context


class BotBaseException(commands.CommandError, ABC):

    @abstractmethod
    async def resolve(self, ctx: Context):
        pass
