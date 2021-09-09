__version__ = "0.1"
__author__ = "Eetu Asikainen"

from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from discord import Embed

from Bot.DataClasses.Displayable import Displayable
from Bot.Core.BotDependencyInjector import BotDependencyInjector


T = TypeVar('T', bound=Displayable)  # pylint: disable=invalid-name


# this class is critical for making cogs easily testable and thus it's ok to have some static functions
# noinspection PyMethodMayBeStatic
@BotDependencyInjector.instance
class ResponseBuilder(Generic[T]):

    async def send(self, ctx, text=None, *, displayable: T = None, delete_after=None):
        if displayable is None:
            await ctx.send(text, delete_after=delete_after)
        else:
            await ctx.send(text, embed=self.build(displayable), delete_after=delete_after)

    @abstractmethod
    def build(self, displayable: T) -> Embed:  # pragma: no-cover
        pass
