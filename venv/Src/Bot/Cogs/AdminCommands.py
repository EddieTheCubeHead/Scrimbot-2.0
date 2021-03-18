import discord
from discord.ext import commands

class AdminCommands(commands.Cog):
    def __init__(self, client):
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

    @register.error()
    async def register_error(self, ctx):
        if isinstance(error, commands.UserInputError):
            self.client.error_msg()