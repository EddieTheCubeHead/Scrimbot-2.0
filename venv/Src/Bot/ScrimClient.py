__version__ = "0.1"
__author__ = "Eetu Asikainen"

import json
import logging
import os

import discord
from discord.ext import commands

from Src.Database.DatabaseManager import DatabaseManager

class ScrimClient(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=self.get_prefix, intents = discord.Intents.default())

        # Logging setup code stolen from the original Scrim-Bot, that was probably stolen from somewhere else
        logger = logging.getLogger('discord')
        logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(filename='scrim_bot.log', encoding='utf-8', mode='w')
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        logger.addHandler(handler)

        # Cogs are loaded as extensions so I can abuse the ability to reload them without restarting the bot if I decide
        # to try and automate the development more in the future.
        self.__setup_cogs()

        self.database_manager = DatabaseManager()

        with open("secrets.json") as secret_file:
            self.__secrets = json.load(secret_file)

        self.run(self.__secrets["token"])

    async def get_prefix(self, message: discord.Message):
        return "/"

    def __setup_cogs(self):
        cog_files = []

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
        await self.temp_msg(ctx, forward_msg, delete_delay = 24.0)

    async def on_ready(self):
        print(f"Successfully logged in as {self.user.name}, version {__version__}")

if __name__ == "__main__":
    client = ScrimClient()