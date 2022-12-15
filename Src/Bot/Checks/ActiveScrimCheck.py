__version__ = "0.1"
__author__ = "Eetu Asikainen"

from hintedi import HinteDI

from Src.Bot.Checks.CheckBase import CheckBase
from Src.Bot.Converters.ScrimConverter import ScrimConverter
from Src.Bot.Core.ScrimContext import ScrimContext
from Src.Bot.Exceptions.BotMissingScrimException import BotMissingScrimException


class ActiveScrimCheck(CheckBase):

    @HinteDI.inject
    async def check(self, ctx: ScrimContext, scrim_converter: ScrimConverter):
        if not scrim_converter.exists(ctx.channel.id):
            raise BotMissingScrimException(ctx.channel.id)
        return True

