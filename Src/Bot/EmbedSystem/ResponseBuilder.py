__version__ = "0.1"
__author__ = "Eetu Asikainen"

from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from discord import Embed, Message
from discord.ext.commands import Context

from Bot.DataClasses.DataClass import DataClass
from Bot.Core.BotDependencyInjector import BotDependencyInjector


T = TypeVar('T', bound=DataClass)  # pylint: disable=invalid-name


# this class is critical for making cogs easily testable and thus it's ok to have some static functions
# noinspection PyMethodMayBeStatic
@BotDependencyInjector.instance
class ResponseBuilder(Generic[T]):

    async def send(self, ctx: Context, text=None, *, displayable: T = None, delete_after=None, delete_parent=True) \
            -> Message:
        if delete_parent:
            await ctx.message.delete()
        if displayable is None:
            return await ctx.send(text, delete_after=delete_after)
        else:
            return await ctx.send(text, embed=self.build(ctx, displayable), delete_after=delete_after)

    @abstractmethod
    def build(self, ctx: Context, displayable: T) -> Embed:  # pragma: no cover
        pass
