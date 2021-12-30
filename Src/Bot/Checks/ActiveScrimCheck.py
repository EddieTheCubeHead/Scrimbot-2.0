__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord.ext.commands import Context

from Bot.Checks.CheckBase import CheckBase


class ActiveScrimCheck(CheckBase):

    @classmethod
    async def check(cls, ctx: Context):
        return True
