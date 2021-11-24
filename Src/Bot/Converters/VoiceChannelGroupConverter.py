__version__ = "ver"
__author__ = "Eetu Asikainen"

from discord.ext.commands import Context

from Bot.Converters.ConverterBase import ConverterBase
from Bot.Converters.Helpers.ChannelGroupParser import ChannelGroupParser
from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.DataClasses.VoiceChannel import VoiceChannel
from Bot.Exceptions.BotBaseUserException import BotBaseUserException
from Bot.Exceptions.BotConversionFailureException import BotConversionFailureException
from Database.DatabaseConnections.ScrimChannelConnection import ScrimChannelConnection

DO_CONVERSION_STRINGS = ["auto", "group", "category", "from_group", "from_category"]


@BotDependencyInjector.singleton
class VoiceChannelGroupConverter(ConverterBase[VoiceChannel]):

    @BotDependencyInjector.inject
    def __init__(self, connection: ScrimChannelConnection, parser: ChannelGroupParser):
        super().__init__(connection)
        self._parser = parser

    async def convert(self, ctx: Context, argument: str) -> list[VoiceChannel]:
        if argument in DO_CONVERSION_STRINGS:
            return self._get_category_channels(ctx)

    def _get_category_channels(self, ctx: Context) -> list[VoiceChannel]:
        if not ctx.channel.category:
            raise BotBaseUserException(f"Cannot automatically assign voice channels from category because channel "
                                       f"'{ctx.channel.name}' doesn't belong in a category")
        return self._build_channels(ctx)

    def _build_channels(self, ctx: Context) -> list[VoiceChannel]:
        voice_channels = ctx.channel.category.voice_channels
        if len(voice_channels) == 1:
            return [VoiceChannel(voice_channels[0].id, ctx.channel.id, 0)]
        elif len(voice_channels) > 1:
            parsed_channels = self._parser.parse(ctx.channel.category)
            return [VoiceChannel(channel.id, ctx.channel.id, team) for channel, team in parsed_channels]
