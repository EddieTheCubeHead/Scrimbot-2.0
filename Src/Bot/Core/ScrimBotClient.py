__version__ = "0.1"
__author__ = "Eetu Asikainen"

import asyncio
import logging
import os
from pathlib import Path
from sys import argv

import discord
from discord.ext import commands
from discord.ext.commands import Context

from Bot.Converters.GameConverter import GameConverter
from Bot.Converters.GuildConverter import GuildConverter
from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.Core.ContextProvider import ContextProvider
from Bot.Core.Logging.BotClientLogger import BotClientLogger
from Bot.Exceptions.BotBaseException import BotBaseException
from Bot.Exceptions.BotBaseInternalSystemException import BotBaseInternalSystemException
from Bot.Exceptions.BotUnrecognizedCommandException import BotUnrecognizedCommandException
from Configs.Config import Config
from Bot.Logic.BotHelpCommand import BotHelpCommand
from Src.Bot.Exceptions.BotBaseInternalClientException import BotBaseInternalClientException
from Src.Bot.Exceptions.BotBaseUserException import BotBaseUserException
from Bot.Core.ScrimContext import ScrimContext


class ScrimBotClient(commands.Bot):
    """The class that implements the discord.py bot class. The heart of the bot."""

    @BotDependencyInjector.inject
    def __init__(self, config: Config, logger: BotClientLogger, context_provider: ContextProvider,
                 guild_converter: GuildConverter, game_converter: GameConverter, event_loop=None):
        """The constructor of ScrimClient. Running this only creates an instance, setup_cogs and start_bot are still
        required to be ran for the bot to start."""

        intents = discord.Intents.default()
        intents.members = True
        super().__init__(command_prefix=self.get_prefix, intents=intents, help_command=BotHelpCommand(), loop=event_loop)

        self.connected = asyncio.Event()
        self.context_provider = context_provider
        self.guild_converter = guild_converter
        self.game_converter = game_converter
        self.config = config
        self.logger = logger
        self.description = "A discord bot for organizing scrims."

    def setup_logging(self):
        loggers = (logging.getLogger("discord"), logging.getLogger("sqlalchemy.engine"))
        for logger in loggers:
            logger.addHandler(self.logger.handler)
            logger.setLevel(logging.DEBUG)

    def setup_cogs(self):
        """A private helper method for loading and starting all the cogs of the bot."""

        parent_path = rf"{Path(os.path.dirname(__file__)).parent}"
        for cog in os.listdir(rf"{parent_path}\Cogs"):
            if cog[-3:] == ".py" and not cog.startswith("_"):
                self.load_extension(f".{cog[:-3]}", package="Bot.Cogs")

    def load_games(self):
        self.game_converter.init_games(self.config.games_dict)

    async def start_bot(self):
        print("Attempting a connection to Discord...")
        await self.start(self.config.token)

    async def get_prefix(self, message: discord.Message):
        """An overridden method from the base class required for custom prefix support"""

        guild_data = self.guild_converter.get_guild(message.guild.id)
        return guild_data.prefixes or self.config.default_prefix

    async def get_deletion_time(self, guild: discord.Guild) -> int:
        """A method that returns the idle scrim deletion time for a given guild."""

        guild_data = await self.guild_converter.get_guild(guild.id)
        return guild_data.scrim_timeout or self.config.default_timeout

    async def get_context(self, message: discord.Message, *, cls=None) -> ScrimContext:
        """An override for get context to facilitate custom context for the bot"""

        return await self.context_provider.get_context(super(), message)

    async def invoke(self, ctx: Context):
        if ctx.command:
            await super().invoke(ctx)
        elif ctx.invoked_with:
            raise BotUnrecognizedCommandException(ctx)

    async def on_command_error(self, context: commands.Context, exception: Exception):
        """An override for the default discord.py command error handler"""

        if isinstance(exception, BotBaseException):
            await exception.resolve(context)

        elif isinstance(exception, BotBaseInternalSystemException):
            exception.resolve()

        else:
            self.logger.critical(str(exception))

    async def _handle_user_error(self, ctx: commands.Context, exception: BotBaseUserException):
        """The default way to handle user related exceptions for commands

        :param ctx: The context of the raised error
        :type ctx: commands.Context
        :param exception: The raised exception
        :type exception: BotBaseUserException
        """

        forward_msg = f"{exception.get_header()} {exception.get_description()}{exception.get_help_portion(ctx)}"
        await self.temp_msg(ctx, forward_msg, delete_delay=32.0)

    async def _handle_internal_error(self, ctx: commands.Context, exception: BotBaseInternalClientException):
        """The default way to handle internal exceptions for commands

        :param ctx: The context of the raised error
        :type ctx: commands.Context
        :param exception: The raised exception
        :type exception: BotBaseInternalClientException
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
        :type exception: BotBaseInternalClientException
        """

        if isinstance(exception, BotBaseUserException):
            temporary_message = await react.message.channel.send(f"{exception.get_header()} "
                                                                 f"{exception.get_description()}")
            await temporary_message.delete(delay=8)

        elif isinstance(exception, BotBaseInternalClientException) and exception.log or \
                isinstance(exception, discord.DiscordException) and not isinstance(exception, BotBaseInternalClientException):

            self.logger.warning(f"reaction: '{react.emoji}' in message: '{react.message.content}' "
                                f"added by: '{user}' caused the exception: {exception}")

    async def on_ready(self):
        """Bot initialization logic. Currently just functions to inform the user the bot is connected."""

        print(f"Successfully logged in as {self.user.name}, with version {__version__}")
        self.connected.set()


if __name__ == "__main__":  # pragma: no cover
    loop = asyncio.get_event_loop()
    client = ScrimBotClient()
    client.setup_logging()
    client.load_games()
    client.setup_cogs()
    loop.run_until_complete(client.start_bot())
