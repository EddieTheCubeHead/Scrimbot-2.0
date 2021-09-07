__version__ = "0.1"
__author__ = "Eetu Asikainen"

import asyncio
import logging
import os
import sys
from pathlib import Path

import discord
from discord.ext import commands

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.Converters.ScrimChannelConverter import ScrimChannelConverter
from Bot.Converters.GameConverter import GameConverter
from Bot.DataClasses.Guild import Guild
from Bot.DataClasses.Prefix import Prefix
from Database.DatabaseConnections import GameConnection
from Configs.Config import Config
from Bot.Logic.BotHelpCommand import BotHelpCommand
from Src.Bot.Exceptions.BotBaseInternalException import BotBaseInternalException
from Src.Bot.Exceptions.BotBaseUserException import BotBaseUserException
from Bot.Core.ScrimContext import ScrimContext


def _setup_logging(folder_path):
    # Logging setup code stolen from discord.py docs
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename=f'{folder_path}/scrim_bot.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s || %(levelname)s || %(name)s || %(message)s'))
    logger.addHandler(handler)
    return logger


class ScrimClient(commands.Bot):
    """The class that implements the discord.py bot class. The heart of the bot."""

    def __init__(self, constructor: BotDependencyInjector, loop=None):
        """The constructor of ScrimClient. Running this starts the bot on the created instance."""

        intents = discord.Intents.default()
        intents.members = True
        super().__init__(command_prefix=self.get_prefix, intents=intents, help_command=BotHelpCommand(), loop=loop)

        self.connected = asyncio.Event()
        self.logger = _setup_logging(Config.file_folder)
        self.description = "A discord bot for organizing scrims."

    def setup_cogs(self):
        """A private helper method for loading and starting all the cogs of the bot."""
        parent_path = rf"{Path(os.path.join(os.path.dirname(__file__))).parent}"
        for cog in os.listdir(rf"{parent_path}\Cogs"):
            if cog[-3:] == ".py" and not cog.startswith("_"):
                self.load_extension(f".{cog[:-3]}", package="Bot.Cogs")

    async def start_bot(self):
        print("Attempting a connection to Discord...")
        await self.start(Config.token)

    async def get_prefix(self, message: discord.Message):
        """An overridden method from the base class required for custom prefix support (TBA)"""

        guild_data = await Guild.convert(message.guild.id)
        return guild_data.prefixes or Config.default_prefix

    async def get_deletion_time(self, guild: discord.Guild) -> int:
        """A method that should return the guild's custom idle scrim deletion time, functionality TBA"""

        guild_data = await Guild.convert(guild.id)
        return guild_data.scrim_timeout or Config.default_timeout

    async def get_context(self, message: discord.Message, *, cls=ScrimContext) -> ScrimContext:
        """An override for get context to facilitate custom context for the bot"""

        return await super().get_context(message, cls=cls)

    async def temp_msg(self, ctx: commands.Context, message: str, *, delete_delay=16.0, delete_original_msg=True):
        """A method for sending a temporary message to the given context.

        args
        ----

        :param ctx: The command invocation context into which the message should be sent
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
            except discord.DiscordException:
                raise BotBaseInternalException(f"Tried to delete message '{ctx.message.content}' with a temp_msg call "
                                               "and failed")

        await temporary_message.delete(delay=delete_delay)

    async def on_command_error(self, context: commands.Context, exception: Exception):
        """An override for the default discord.py command error handler"""

        if isinstance(exception, BotBaseUserException):
            await self._handle_user_error(context, exception)

        elif isinstance(exception, BotBaseInternalException):
            await self._handle_internal_error(context, exception)

        # Special case for unknown commands
        elif isinstance(exception, commands.CommandNotFound):
            await self.temp_msg(context,
                                f"Couldn't find command '{context.message.content.split(' ')[0]}'.\n"
                                f"Use '{context.prefix}help' to see a full list of commands.")

        else:
            self.logger.error(str(exception))
            raise exception

    async def _handle_user_error(self, ctx: commands.Context, exception: BotBaseUserException):
        """The default way to handle user related exceptions for commands

        :param ctx: The context of the raised error
        :type ctx: commands.Context
        :param exception: The raised exception
        :type exception: BotBaseUserException
        """

        forward_msg = f"{exception.get_header()} {exception.get_description()}{exception.get_help_portion(ctx)}"
        await self.temp_msg(ctx, forward_msg, delete_delay=32.0)

    async def _handle_internal_error(self, ctx: commands.Context, exception: BotBaseInternalException):
        """The default way to handle internal exceptions for commands

        :param ctx: The context of the raised error
        :type ctx: commands.Context
        :param exception: The raised exception
        :type exception: BotBaseInternalException
        """

        if exception.log:
            self.logger.warning(f"command: '{ctx.command.name}' invoked as: '{ctx.message.content}' "
                                f"caused the exception: {exception.get_message()}")

    async def handle_react_internal_error(self, react: discord.Reaction, user: discord.Member,
                                          exception: discord.DiscordException):
        """A custom error handler for reaction-event based internal exceptions

        :param react: The reaction associated with the exceptions
        :type react: discord.Reaction
        :param user: The user who added the reaction
        :type user: discord.User
        :param exception: The raised exception
        :type exception: BotBaseInternalException
        """

        if isinstance(exception, BotBaseUserException):
            temporary_message = await react.message.channel.send(f"{exception.get_header()} "
                                                                 f"{exception.get_description()}")
            await temporary_message.delete(delay=8)

        elif isinstance(exception, BotBaseInternalException) and exception.log or \
                isinstance(exception, discord.DiscordException) and not isinstance(exception, BotBaseInternalException):

            self.logger.warning(f"reaction: '{react.emoji}' in message: '{react.message.content}' "
                                f"added by: '{user}' caused the exception: {exception}")

    async def on_ready(self):
        """Bot initialization logic. Currently just functions to inform the user the bot is connected."""

        print(f"Successfully logged in as {self.user.name}, with version {__version__}")
        self.connected.set()


if __name__ == "__main__":
    client = ScrimClient(BotDependencyInjector(f"{Config.file_folder}/{Config.database_name}"))
