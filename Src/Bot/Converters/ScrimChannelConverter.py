__version__ = "0.1"
__author__ = "Eetu Asikainen"

from functools import lru_cache

import discord
from discord.ext.commands import Context

from Bot.Converters.ConverterBase import ConverterBase
from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.DataClasses.ScrimChannel import ScrimChannel
from Bot.DataClasses.VoiceChannel import VoiceChannel
from Bot.Exceptions.BotBaseUserException import BotBaseUserException
from Bot.Exceptions.BotReservedChannelException import BotReservedChannelException
from Database.DatabaseConnections.ScrimChannelConnection import ScrimChannelConnection


@BotDependencyInjector.singleton
class ScrimChannelConverter(ConverterBase[ScrimChannel]):

    connection: ScrimChannelConnection = None

    @BotDependencyInjector.inject
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
            self._validate_voice_channel(channel_id, voice_channel)

    def _validate_voice_channel(self, channel_id, voice_channel):
        reserved_data = self.connection.exists_voice(voice_channel.channel_id)
        if reserved_data:
            raise BotBaseUserException(f"Could not register channel <#{channel_id}> for scrim usage because voice "
                                       f"channel <#{voice_channel.channel_id}> is already associated with scrim "
                                       f"channel <#{reserved_data.channel_id}>.")

    @lru_cache
    def get_from_id(self, channel_id: int):
        return self.connection.get_channel(channel_id)
