__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Bot.Checks.CheckBase import CheckBase
from Bot.Converters.ScrimConverter import ScrimConverter
from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.Core.ScrimContext import ScrimContext
from Bot.Exceptions.BotMissingScrimException import BotMissingScrimException


class ActiveScrimCheck(CheckBase):

    @BotDependencyInjector.inject
    async def check(self, ctx: ScrimContext, scrim_converter: ScrimConverter):
        if not scrim_converter.exists(ctx.channel.id):
            raise BotMissingScrimException(ctx.channel.id)
        return True

