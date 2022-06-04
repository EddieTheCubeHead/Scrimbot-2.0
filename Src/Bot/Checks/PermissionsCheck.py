__version__ = "0.1"
__author__ = "Eetu Asikainen"

from enum import Enum

from discord.ext.commands import Context

from Bot.Checks.CheckBase import CheckBase


class PermissionsCheck(CheckBase):

    async def check(self, ctx: Context):
        pass
