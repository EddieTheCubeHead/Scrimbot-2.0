__version__ = "0.1"
__author__ = "Eetu Asikainen"

from sqlalchemy.exc import NoResultFound

from Bot.Checks.CheckBase import CheckBase
from Bot.Converters.ScrimChannelConverter import ScrimChannelConverter
from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.Core.ScrimContext import ScrimContext
from Bot.Exceptions.BotChannelHasScrimException import BotChannelHasScrimException
from Bot.Exceptions.BotUnregisteredChannelException import BotUnregisteredChannelException


class FreeScrimCheck(CheckBase):

    @BotDependencyInjector.inject
    async def check(self, ctx: ScrimContext, channel_converter: ScrimChannelConverter):
        try:
            channel_converter.get_from_id(ctx.channel.id)
        except NoResultFound as _:
            raise BotUnregisteredChannelException(ctx.channel.id)
        if ctx.scrim:
            raise BotChannelHasScrimException(ctx.channel.id)
        return True
