__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord.ext.commands import Context
from hintedi import HinteDI

from Src.Bot.Converters.ConverterBase import ConverterBase
from Src.Bot.DataClasses.ScrimChannel import ScrimChannel
from Src.Bot.DataClasses.VoiceChannel import VoiceChannel
from Src.Bot.Exceptions.BotBaseRespondToContextException import BotBaseRespondToContextException
from Src.Bot.Exceptions.BotReservedChannelException import BotReservedChannelException
from Src.Database.DatabaseConnections.ScrimChannelConnection import ScrimChannelConnection


@HinteDI.singleton
class ScrimChannelConverter(ConverterBase[ScrimChannel]):

    connection: ScrimChannelConnection = None

    @HinteDI.inject
    def __init__(self, connection: ScrimChannelConnection):
        super().__init__(connection)

    async def convert(self, ctx: Context, argument: str) -> ScrimChannel:
        return self.get_from_id(int(argument))

    def add(self, channel_id: int, guild_id: int, *voice_channels: VoiceChannel):
        self._validate_free_channels(channel_id, *voice_channels)
        channel = ScrimChannel(channel_id, guild_id, *voice_channels)
        self.connection.add_channel(channel)
        return channel

    def _validate_free_channels(self, channel_id, *voice_channels: VoiceChannel):
        if self.connection.exists_text(channel_id):
            raise BotReservedChannelException(channel_id)
        for voice_channel in voice_channels:
            self._validate_voice_channel(voice_channel)

    def _validate_voice_channel(self, voice_channel):
        reserved_data = self.connection.exists_voice(voice_channel.channel_id)
        if reserved_data:
            raise BotReservedChannelException(voice_channel.channel_id, parent_channel_id=reserved_data.channel_id)

    def get_from_id(self, channel_id: int):
        return self.connection.get_channel(channel_id)
