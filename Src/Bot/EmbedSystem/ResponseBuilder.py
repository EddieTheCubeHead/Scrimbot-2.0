__version__ = "0.1"
__author__ = "Eetu Asikainen"

from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from discord import Embed, Message, Guild
from discord.ext.commands import Context
from hintedi import HinteDI

from Bot.DataClasses.DataClass import DataClass


T = TypeVar('T', bound=DataClass)  # pylint: disable=invalid-name


# this class is critical for making cogs easily testable and thus it's ok to have some static functions
# noinspection PyMethodMayBeStatic

class _EditWrapperContext(Context):

    def __init__(self, message: Message):
        super().__init__(message=message, prefix="")


@HinteDI.instance
class ResponseBuilder(Generic[T]):

    async def send(self, ctx: Context, text=None, *, displayable: T = None, delete_after=None, delete_parent=True) \
            -> Message:
        if delete_parent:
            await ctx.message.delete()
        if displayable is None:
            return await ctx.send(text, delete_after=delete_after)
        else:
            return await ctx.send(text, embed=self.build(ctx, displayable), delete_after=delete_after)

    async def edit(self, original: Message, text=None, *, displayable: T = None) -> Message:
        if displayable is None:
            return await original.edit(content=text)
        else:
            return await original.edit(content=text, embed=self.build(_EditWrapperContext(original), displayable))

    @abstractmethod
    def build(self, ctx: Context, displayable: T) -> Embed:  # pragma: no cover
        pass
