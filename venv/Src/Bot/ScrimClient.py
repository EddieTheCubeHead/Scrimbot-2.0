__version__ = "0.1"
__author__ = "Eetu Asikainen"

import json
import logging
import os

import discord
from discord.ext import commands

from Src.Bot.DataClasses.Game import Game
from Src.Database.DatabaseManager import DatabaseManager
from Src.Bot.DataClasses.Scrim import Scrim

class ScrimClient(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(command_prefix=self.get_prefix, intents = intents)

        # Logging setup code stolen from the original Scrim-Bot, that was probably stolen from somewhere else
        logger = logging.getLogger('discord')
        logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(filename='scrim_bot.log', encoding='utf-8', mode='w')
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        logger.addHandler(handler)

        self.database_manager = DatabaseManager()
        Scrim.set_database_manager(self.database_manager)

        # Initializing games into memory
        Game.init_games(self.database_manager.games_init_generator())

        # Cogs are loaded as extensions so I can abuse the ability to reload them without restarting the bot if I decide
        # to try and automate the deployment pipeline more in the future.
        self._setup_cogs()

        with open("secrets.json") as secret_file:
            self._secrets = json.load(secret_file)

        self.run(self._secrets["token"])

    async def get_prefix(self, message: discord.Message):
        return "/"

    async def get_deletion_time(self, context: commands.Context):
        return 15

    def _setup_cogs(self):
        for cog in os.listdir("Cogs"):
            if cog[-3:] == ".py":
                self.load_extension(f"Cogs.{cog[:-3]}")

    async def temp_msg(self, ctx: commands.Context, message: str, *, delete_delay = 8.0, delete_original_msg = True):
        temporary_message = await ctx.send(message)

        if delete_original_msg:
            try:
                await ctx.message.delete()
            except:
                pass

        await temporary_message.delete(delay=delete_delay)

    async def handle_error(self, ctx: commands.Context, error: discord.DiscordException):
        command_str = f"{await self.get_prefix(ctx.message)}help {ctx.command.name}"
        forward_msg = "Error: " + str(error) \
                      + f"\n\nTo get help with this command, use the command '{command_str}'"

        await self.temp_msg(ctx, forward_msg, delete_delay = 32.0)

    async def on_ready(self):
        print(f"Successfully logged in as {self.user.name}, version {__version__}")

if __name__ == "__main__":
    client = ScrimClient()