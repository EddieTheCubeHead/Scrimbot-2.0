__version__ = "0.1"
__author__ = "Eetu Asikainen"

import discord
from discord.ext import commands

# Almost a cyclical import here, but this helps with type hints
import Src.Bot.ScrimClient as sc
from Src.Bot.DataClasses.Scrim import Scrim

class AdminCommands(commands.Cog):
    def __init__(self, client: sc.ScrimClient):
        self._client = client

    def _sanitize_channels__(self, team_1_voice: discord.VoiceChannel, team_2_voice: discord.VoiceChannel,
                              spectator_voice: discord.VoiceChannel):

        if team_1_voice and not team_2_voice:
            raise commands.UserInputError("If you specify a voice channel for team 1 you must also specify a voice \
                                          channel for team 2.")

        if team_1_voice:
            taken_by = self._client.database_manager.check_voice_availability(team_1_voice.id)
            if taken_by:
                error_str = f"Channel {team_1_voice} is already used by a scrim on channel {taken_by[0]}."
                raise commands.UserInputError(error_str)

        if team_2_voice:
            taken_by = self._client.database_manager.check_voice_availability(team_2_voice.id)
            if taken_by:
                error_str = f"Channel {team_2_voice} is already used by a scrim on channel {taken_by[0]}."
                raise commands.UserInputError(error_str)

        if spectator_voice:
            taken_by = self._client.database_manager.check_voice_availability(spectator_voice.id)
            if taken_by:
                error_str = f"Channel {spectator_voice} is already used by a scrim on channel {taken_by[0]}."
                raise commands.UserInputError(error_str)

        # ID declarations outside function call to prevent calling id from None object
        team_1_id = team_1_voice.id if team_1_voice else None
        team_2_id = team_2_voice.id if team_2_voice else None
        spectator_id = spectator_voice.id if spectator_voice else None

        return team_1_id, team_2_id, spectator_id

    @commands.command()
    @commands.guild_only()
    async def register(self, ctx: commands.Context, team_1_voice: discord.VoiceChannel = None,
                       team_2_voice: discord.VoiceChannel = None, spectator_voice: discord.VoiceChannel = None):

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


        team_1_id, team_2_id, spectator_id = self._sanitize_channels__(team_1_voice, team_2_voice, spectator_voice)

        self._client.database_manager.register_scrim_channel(ctx.channel.id, team_1_id, team_2_id, spectator_id)

        Scrim(ctx.channel, team_1_voice, team_2_voice, spectator_voice)

        # I hate constructing strings like this, but backslashes tend to cause unnecessary spaces in the bot message
        success_info = f"Successfully registered the channel '{ctx.channel}' for scrim usage."
        success_info += "\nAssociated voice channels:"
        success_info += f"\nTeam 1: {team_1_voice or 'not set'}"
        success_info += f"\nTeam 2: {team_2_voice or 'not set'}"
        success_info += f"\nSpectators: {spectator_voice or 'not set'}"
        await self._client.temp_msg(ctx, success_info)

    @register.error
    async def register_error(self, ctx: commands.Context, error: discord.DiscordException):
        if isinstance(error, commands.UserInputError):
            await self._client.handle_error(ctx, error)
        else:
            raise error

def setup(client: commands.Bot):
    client.add_cog(AdminCommands(client))
    print(f"Using cog {__name__}, version {__version__}")