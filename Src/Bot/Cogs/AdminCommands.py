__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import Optional

import discord
from discord.ext import commands

from Bot.Core.ScrimClient import ScrimClient
from Bot.DataClasses.ScrimChannel import ScrimChannel
from Src.Bot.Exceptions.BotBaseUserException import BotBaseUserException


class AdminCommands(commands.Cog):
    """A cog housing the upkeep and maintenance related commands of the bot

    Commands
    -------
    register(ctx, team_1_voice, team_2_voice, spectator_voice)
        A command to register a channel as a channel that can be used for scrims
    """

    def __init__(self, client: ScrimClient):
        """The constructor of the AdminCommands cog.

        args
        ----

        :param client: The client instance associated with this cog.
        :type client: ScrimClient
        """

        self._client = client

    def _sanitize_channels(self, team_1_voice: Optional[discord.VoiceChannel],
                           team_2_voice: Optional[discord.VoiceChannel],
                           spectator_voice: Optional[discord.VoiceChannel]) \
            -> (Optional[int], Optional[int], Optional[int]):
        """A private method that validates the given voice channels as free and returns their ids

        args
        ----

        :param team_1_voice: The voice channel designated for team 1
        :type team_1_voice: Optional[discord.VoiceChannel]
        :param team_2_voice: The voice channel designated for team 2
        :type team_2_voice: Optional[discord.VoiceChannel]
        :param spectator_voice: The voice channel designated for spectators
        :type spectator_voice: Optional[discord.VoiceChannel]
        :return: Channel id's corresponding to the input channels
        :rtype: (Optional[int], Optional[int], Optional[int])
        """

        if team_1_voice and not team_2_voice:
            raise BotBaseUserException("If you specify a voice channel for team 1 you must also specify a voice "
                                       "channel for team 2.")

        for channel in (team_1_voice, team_2_voice, spectator_voice):
            if channel:
                self._check_channel_availability(channel)

        # ID declarations outside function call to prevent calling id from None object
        team_1_id: Optional[int] = team_1_voice.id if team_1_voice else None
        team_2_id: Optional[int] = team_2_voice.id if team_2_voice else None
        spectator_id: Optional[int] = spectator_voice.id if spectator_voice else None

        return team_1_id, team_2_id, spectator_id

    def _check_channel_availability(self, channel: discord.VoiceChannel):
        taken_by = self._client.database_manager.check_voice_availability(channel.id)
        if taken_by:
            error_str = f"Channel {channel} is already used by a scrim on channel {taken_by[0]}."
            raise BotBaseUserException(error_str)

    @commands.command()
    @commands.guild_only()
    async def register(self, ctx: commands.Context, team_1_voice: discord.VoiceChannel = None,
                       team_2_voice: discord.VoiceChannel = None, spectator_voice: discord.VoiceChannel = None):
        """A command that registers a channel as viable for scrim usage and assigns associated voice channels.

        args
        ----

        :param ctx: The invocation context of the command
        :type ctx: commands.Context
        :param team_1_voice: The voice channel assigned to team 1. If blank tries to find from channel group
        :type team_1_voice: Optional[discord.VoiceChannel]
        :param team_2_voice: The voice channel assigned to team 2. If blank tries to find from channel group
        :type team_2_voice: Optional[discord.VoiceChannel]
        :param spectator_voice: The voice channel assigned to spectators. If blank tries to find from channel group
        :type spectator_voice: Optional[discord.VoiceChannel]
        """

        # Try to automatically assign voice channels if the category is of the right size
        if not team_1_voice:

            if 2 <= len(ctx.channel.category.voice_channels) <= 4 and len(ctx.channel.category.text_channels) <= 3:
                voice_candidates = ctx.channel.category.voice_channels

                for channel in voice_candidates:
                    if self._client.database_manager.check_voice_availability(channel.id):
                        break

                else:
                    if len(voice_candidates) == 2:
                        voice_candidates.append(None)

                    team_1_voice, team_2_voice, spectator_voice = voice_candidates[:3]

        team_1_id, team_2_id, spectator_id = self._sanitize_channels(team_1_voice, team_2_voice, spectator_voice)
        self._client.database_manager.register_scrim_channel(ctx.channel.id, team_1_id, team_2_id, spectator_id)
        ScrimChannel(ctx.channel, team_1_voice, team_2_voice, spectator_voice)

        # I hate constructing strings like this, but backslashes tend to cause unnecessary spaces in the bot message
        success_info = f"Successfully registered the channel '{ctx.channel}' for scrim usage."
        success_info += "\nAssociated voice channels:"
        success_info += f"\nTeam 1: {team_1_voice or 'not set'}"
        success_info += f"\nTeam 2: {team_2_voice or 'not set'}"
        success_info += f"\nSpectators: {spectator_voice or 'not set'}"
        await self._client.temp_msg(ctx, success_info)


def setup(client: ScrimClient):
    """A method for adding the cog to the bot

    args
    ----

    :param client: The instance of the bot the cog should be added into
    :type client: ScrimClient
    """

    client.add_cog(AdminCommands(client))
    print(f"Using cog {__name__}, with version {__version__}")
