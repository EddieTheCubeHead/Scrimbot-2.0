__version__ = "0.1"
__author__ = "Eetu Asikainen"

from abc import ABC, abstractmethod

from discord.ext.commands import check, Command, Context


class CheckBase(ABC):

    @classmethod
    def decorate(cls):
        async def check_decorator(ctx: Context):
            return cls.check(ctx)
        return check(check_decorator)

    @classmethod
    @abstractmethod
    def check(cls, ctx: Context):
        pass
