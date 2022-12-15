__version__ = "0.1"
__author__ = "Eetu Asikainen"

from sqlalchemy.exc import NoResultFound
from hintedi import HinteDI

from Src.Bot.Checks.CheckBase import CheckBase
from Src.Bot.Converters.ScrimChannelConverter import ScrimChannelConverter
from Src.Bot.Converters.ScrimConverter import ScrimConverter
from Src.Bot.Core.ScrimContext import ScrimContext
from Src.Bot.Exceptions.BotChannelHasScrimException import BotChannelHasScrimException
from Src.Bot.Exceptions.BotUnregisteredChannelException import BotUnregisteredChannelException


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
