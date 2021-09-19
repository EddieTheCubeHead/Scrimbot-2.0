__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord.ext import commands
from discord.ext.commands import Greedy

from Bot.Converters.ScrimChannelConverter import ScrimChannelConverter
from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.Core.ScrimClient import ScrimClient
from Bot.DataClasses.VoiceChannel import VoiceChannel
from Bot.EmbedSystem.ScrimChannelEmbedBuilder import ScrimChannelEmbedBuilder
from Bot.Logic.ScrimChannelManager import ScrimChannelManager


class ScrimChannelCommands(commands.Cog):
    """A cog housing the channel maintenance related commands of the bot"""

    @BotDependencyInjector.inject
    def __init__(self, response_builder: ScrimChannelEmbedBuilder, channel_converter: ScrimChannelConverter,
                 scrim_channel_manager: ScrimChannelManager):
        self._response_builder: ScrimChannelEmbedBuilder = response_builder
        self._channel_converter: ScrimChannelConverter = channel_converter
        self._channel_manager: scrim_channel_manager = scrim_channel_manager

    @commands.command()
    @commands.guild_only()
    async def register(self, ctx: commands.Context, voice_channels: Greedy[VoiceChannel]):
        """A command that registers a channel as viable for scrim usage and assigns associated voice channels.

        args
        ----

        :param ctx: The invocation context of the command
        :type ctx: commands.Context
        :param voice_channels: The voice channels that should be associated with this scrim
        :type voice_channels: list[VoiceChannel]
        """

        voice_channels = self._channel_manager.enumerate_teams(voice_channels)
        created = self._channel_converter.add(ctx.channel.id, ctx.guild.id, *voice_channels)
        await self._response_builder.send(ctx, displayable=created)


def setup(client: ScrimClient):
    client.add_cog(ScrimChannelCommands())
    print(f"Using cog {__name__}, with version {__version__}")
