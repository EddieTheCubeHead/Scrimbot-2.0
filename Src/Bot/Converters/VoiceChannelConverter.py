__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord.ext.commands import converter, Context
from hintedi import HinteDI

from Src.Bot.Converters.ConverterBase import ConverterBase
from Src.Bot.DataClasses.VoiceChannel import VoiceChannel
from Src.Database.DatabaseConnections.ScrimChannelConnection import ScrimChannelConnection


_LOBBY_CHANNEL_PREFIX: str = "l:"


@HinteDI.singleton
class VoiceChannelConverter(ConverterBase[VoiceChannel]):

    connection: ScrimChannelConnection = None

    @HinteDI.inject
    def __init__(self, connection: ScrimChannelConnection):
        super().__init__(connection)

    async def convert(self, ctx: Context, argument: str) -> VoiceChannel:
        channel_team = None
        if argument.startswith(_LOBBY_CHANNEL_PREFIX):
            channel_team = 0
            argument = argument[2:]
        channel = await converter.VoiceChannelConverter().convert(ctx, argument)
        return VoiceChannel(channel.id, ctx.channel.id, channel_team)
