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
from Src.Bot.DataClasses.BotHelpCommand import BotHelpCommand
from Src.Bot.Exceptions.BotBaseInternalException import BotBaseInternalException
from Src.Bot.Exceptions.BotBaseUserException import BotBaseUserException

class ScrimClient(commands.Bot):
    """The class that implements the discord.py bot class. The heart of the bot."""

    def __init__(self):
        """The constructor of ScrimClient. Running this starts the bot on the created instance."""

        intents = discord.Intents.default()
        intents.members = True
        super().__init__(command_prefix=self.get_prefix, intents = intents, help_command=BotHelpCommand())

        # Logging setup code stolen from discord.py docs
        self.logger = logging.getLogger('discord')
        self.logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(filename='scrim_bot.log', encoding='utf-8', mode='w')
        handler.setFormatter(logging.Formatter('%(asctime)s || %(levelname)s || %(name)s || %(message)s'))
        self.logger.addHandler(handler)

        self.database_manager = DatabaseManager()
        Scrim.set_database_manager(self.database_manager)

        # Initializing games into memory
        Game.init_games(self.database_manager.games_init_generator())

        # Cogs are loaded as extensions so I can abuse the ability to reload them without restarting the bot if I decide
        # to try and automate the deployment pipeline more in the future.
        self._setup_cogs()

        with open("secrets.json") as secret_file:
            self._secrets = json.load(secret_file)

        self.description = "A discord bot for organizing scrims."
        self.run(self._secrets["token"])

    async def get_prefix(self, message: discord.Message):
        """An overridden method from the base class required for custom prefix support (TBA)"""

        return "/"

    async def get_deletion_time(self, context: commands.Context):
        """A method that should return the guild's custom idle scrim deletion time, functionality TBA"""

        return 15

    def _setup_cogs(self):
        """A private helper method for loading and starting all the cogs of the bot."""

        for cog in os.listdir("Cogs"):
            if cog[-3:] == ".py":
                self.load_extension(f"Cogs.{cog[:-3]}")

    async def temp_msg(self, ctx: commands.Context, message: str, *, delete_delay = 16.0, delete_original_msg = True):
        """A method for sending a temporary message to the given context.

        args
        ----

        :param ctx: The command invokation context into which the message should be sent
        :type ctx: commands.Context
        :param message: The message content
        :type message: str

        kwargs
        ------

        :param delete_delay: The delay after which the message should be deleted
        :type delete_delay: float
        :param delete_original_msg: Whether to also delete the original message from the context
        :type delete_original_msg: bool
        """

        temporary_message = await ctx.send(message)

        if delete_original_msg:
            try:
                await ctx.message.delete()
            except:
                pass

        await temporary_message.delete(delay=delete_delay)

    async def on_command_error(self, context: commands.Context, exception: Exception):
        """An override for the default discord.py command error handler"""

        if isinstance(exception, BotBaseUserException):
            await self._handle_user_error(context, exception)
        elif isinstance(exception, BotBaseInternalException):
            await self._handle_internal_error(context, exception)
        else:
            raise exception

    async def _handle_user_error(self, ctx: commands.Context, exception: BotBaseUserException):
        """The default way to handle user related exceptions for commands

        :param ctx: The context of the raised error
        :type ctx: commands.Context
        :param error: The raised error
        :type error: BotBaseUserException
        """

        command_str = f"{ctx.prefix}help {ctx.command.name}"
        forward_msg = f"{exception.get_header()} {exception.get_description()}" \
                      + f"\n\nTo get help with this command, use the command '{command_str}'"

        await self.temp_msg(ctx, forward_msg, delete_delay = 32.0)

    async def _handle_internal_error(self, ctx: commands.Context, exception: BotBaseInternalException):
        """The default way to handle internal exceptions for commands

        :param ctx: The context of the raised error
        :type ctx: commands.Context
        :param error: The raised error
        :type error: BotBaseInternalException
        """

        self.logger.error(f"command: '{ctx.command.name}' invoked as: '{ctx.message.content}' " + \
                          f"error: {exception.get_message()}")

    async def on_ready(self):
        """Bot initialization logic. Currently just functions to inform the user the bot is connected."""
        print(f"Successfully logged in as {self.user.name}, version {__version__}")

if __name__ == "__main__":
    client = ScrimClient()
