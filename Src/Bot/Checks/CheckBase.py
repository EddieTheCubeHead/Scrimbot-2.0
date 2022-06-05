__version__ = "0.1"
__author__ = "Eetu Asikainen"

from abc import ABC, abstractmethod

from discord.ext.commands import check, Context


class CheckBase(ABC):

    def __call__(self, func):
        @check
        async def check_wrapper(ctx: Context):
            return await self.check(ctx)
        return check_wrapper(func)

    @abstractmethod
    async def check(self, ctx: Context):  # pragma: no cover
        pass
