__version__ = "0.1"
__author__ = "Eetu Asikainen"

from abc import ABC, abstractmethod

from discord.ext.commands import check, Context


class CheckBase(ABC):

    @classmethod
    def decorate(cls):
        async def check_decorator(ctx: Context):
            return await cls.check(ctx)
        return check(check_decorator)

    @classmethod
    @abstractmethod
    async def check(cls, ctx: Context):  # pragma: no cover
        pass
