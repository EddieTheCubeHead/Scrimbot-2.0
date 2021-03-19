__version__ = "0.1"
__author__ = "Eetu Asikainen"

import discord
from discord.ext import commands

from Src.Bot.ScrimClient import ScrimClient
import Src.Bot.Checks as checks
from Src.Bot.DataClasses.Game import Game
from Src.Bot.DataClasses.Scrim import Scrim

class ScrimCommands(commands.Cog):
    def __init__(self, client: ScrimClient):
        self._client = client

    @commands.command(aliases=['s'])
    @commands.guild_only()
    @checks.free_scrim()
    async def scrim(self, ctx: commands.Context, game: Game, deletion_time: int = 0):
        scrim = await Scrim.get_scrim(ctx)
        deletion_time = deletion_time or self._client.get_deletion_time(ctx)
        await scrim.create(ctx, game, deletion_time)
        await ctx.message.delete()

def setup(client: commands.Bot):
    client.add_cog(ScrimCommands(client))
    print(f"Using cog {__name__}, version {__version__}")