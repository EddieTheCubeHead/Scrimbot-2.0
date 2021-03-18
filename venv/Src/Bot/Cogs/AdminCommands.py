__version__ = "0.1"
__author__ = "Eetu Asikainen"

import discord
from discord.ext import commands

# Almost a cyclical import here, but this helps with type hints
import Src.Bot.ScrimClient as sc

class AdminCommands(commands.Cog):
    def __init__(self, client: sc.ScrimClient):
        self.client = client

    @commands.command()
    @commands.guild_only()
    async def register(self, ctx: commands.Context, team_1_voice: discord.VoiceChannel = None,
                       team_2_voice: discord.VoiceChannel = None, spectator_voice: discord.VoiceChannel = None):

        if team_1_voice and not team_2_voice:
            raise commands.UserInputError("If you specify a voice channel for team 1 you must also specify a voice \
                                          channel for team 2.")

        # ID declarations outside function call to prevent calling id from None object
        team_1_id = team_1_voice.id if team_1_voice else None
        team_2_id = team_2_voice.id if team_2_voice else None
        spectator_id = spectator_voice.id if spectator_voice else None

        self.client.database_manager.register_scrim_channel(ctx.channel.id, team_1_id, team_2_id, spectator_id)

        # I hate constructing strings like this, but backslashes tend to cause unnecessary spaces in the bot message
        success_info = f"Successfully registered the channel '{ctx.channel}' for scrim usage."
        success_info += "\nAssociated voice channels:"
        success_info += f"\nTeam 1: {team_1_voice or 'not set'}"
        success_info += f"\nTeam 2: {team_2_voice or 'not set'}"
        success_info += f"\nSpectators: {spectator_voice or 'not set'}"
        await self.client.temp_msg(ctx, success_info)

    @register.error
    async def register_error(self, ctx: commands.Context, error: discord.DiscordException):
        await self.client.handle_error(ctx, error)

def setup(client: commands.Bot):
    print(f"Using cog {__name__}, version {__version__}")
    client.add_cog(AdminCommands(client))