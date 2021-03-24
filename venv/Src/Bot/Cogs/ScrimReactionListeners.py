__version__ = "0.1"
__author__ = "Eetu Asikainen"

import discord
from discord.ext import commands

from Src.Bot.ScrimClient import ScrimClient
from Src.Bot.DataClasses.Scrim import Scrim
from Src.Bot.DataClasses.ScrimTeam import ScrimTeam

class ScrimReactionListeners(commands.Cog):
    def __init__(self, client: ScrimClient):
        self._client = client

    @commands.Cog.listener()
    async def on_reaction_add(self, react: discord.Reaction, user: discord.Member):
        if user.bot:
            return

        scrim = await Scrim.get_from_reaction(react)
        if not scrim:
            return

        try:
            if react.emoji == "\U0001F3AE":
                await scrim.add_player(user)

            elif react.emoji == "\U0001F441":
                await scrim.add_spectator(user)

            elif react.emoji == "1\u20E3":
                await scrim.set_team(user, ScrimTeam.TEAM1)

            elif react.emoji == "2\u20E3":
                await scrim.set_team(user, ScrimTeam.TEAM2)

            elif react.emoji == "\U0001F451":
                await scrim.add_captain(user)

        # TODO: figure out reaction-based error handling
        except commands.CommandError:
            pass

    @commands.Cog.listener()
    async def on_reaction_remove(self, react: discord.Reaction, user: discord.Member):
        if user.bot:
            return

        scrim = await Scrim.get_from_reaction(react)
        if not scrim:
            return

        try:
            if react.emoji == "\U0001F3AE":
                await scrim.remove_player(user)

            elif react.emoji == "\U0001F441":
                await scrim.remove_spectator(user)

            elif react.emoji == "1\u20E3":
                await scrim.set_team(user, ScrimTeam.TEAMLESS)

            elif react.emoji == "2\u20E3":
                await scrim.set_team(user, ScrimTeam.TEAMLESS)

            elif react.emoji == "\U0001F451":
                await scrim.remove_captain(user)

        # TODO: figure out reaction-based error handling
        except commands.CommandError:
            pass


def setup(client: commands.Bot):
    client.add_cog(ScrimReactionListeners(client))
    print(f"Using cog {__name__}, version {__version__}")