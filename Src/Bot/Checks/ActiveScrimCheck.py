__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Bot.Checks.CheckBase import CheckBase
from Bot.Core.ScrimContext import ScrimContext
from Bot.Exceptions.BotMissingScrimException import BotMissingScrimException


class ActiveScrimCheck(CheckBase):

    @classmethod
    async def check(cls, ctx: ScrimContext):
        if not ctx.scrim:
            raise BotMissingScrimException(ctx.channel.id)
        return True

