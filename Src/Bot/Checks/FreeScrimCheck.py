__version__ = "0.1"
__author__ = "Eetu Asikainen"

from sqlalchemy.exc import NoResultFound
from hintedi import HinteDI

from Bot.Checks.CheckBase import CheckBase
from Bot.Converters.ScrimChannelConverter import ScrimChannelConverter
from Bot.Converters.ScrimConverter import ScrimConverter
from Bot.Core.ScrimContext import ScrimContext
from Bot.Exceptions.BotChannelHasScrimException import BotChannelHasScrimException
from Bot.Exceptions.BotUnregisteredChannelException import BotUnregisteredChannelException


class FreeScrimCheck(CheckBase):

    @HinteDI.inject
    async def check(self, ctx: ScrimContext, channel_converter: ScrimChannelConverter, scrim_converter: ScrimConverter):
        try:
            channel_converter.get_from_id(ctx.channel.id)
        except NoResultFound as _:
            raise BotUnregisteredChannelException(ctx.channel.id)
        if scrim_converter.exists(ctx.channel.id):
            raise BotChannelHasScrimException(ctx.channel.id)
        return True
