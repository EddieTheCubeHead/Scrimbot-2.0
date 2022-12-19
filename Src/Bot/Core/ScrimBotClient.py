__version__ = "0.1"
__author__ = "Eetu Asikainen"

import asyncio
import logging
import os
from pathlib import Path

import discord
from discord.ext import commands
from discord.ext.commands import Context
from hintedi import HinteDI

from Src.Bot.Converters.GameConverter import GameConverter
from Src.Bot.Converters.GuildConverter import GuildConverter
from Src.Bot.Core.ContextProvider import ContextProvider
from Src.Bot.Core.Logging.BotClientLogger import BotClientLogger
from Src.Bot.Exceptions.BotBaseContextException import BotBaseContextException
from Src.Bot.Exceptions.BotBaseNoContextException import BotBaseNoContextException
from Src.Bot.Exceptions.BotLoggedNoContextException import BotLoggedNoContextException
from Src.Bot.Exceptions.BotUnrecognizedCommandException import BotUnrecognizedCommandException
from Src.Bot.Logic.DiscordVoiceChannelProvider import DiscordVoiceChannelProvider
from Src.Bot.Logic.ScrimParticipantProvider import ScrimParticipantProvider
from Src.Configs.Config import Config
from Src.Bot.Logic.BotHelpCommand import BotHelpCommand
from Src.Bot.Exceptions.BotLoggedContextException import BotLoggedContextException
from Src.Bot.Exceptions.BotBaseRespondToContextException import BotBaseRespondToContextException
from Src.Bot.Core.ScrimContext import ScrimContext


class ScrimBotClient(commands.Bot):
    """The class that implements the discord.py bot class. The heart of the bot."""

    @HinteDI.inject
    def __init__(self, config: Config, logger: BotClientLogger, context_provider: ContextProvider,
                 guild_converter: GuildConverter, game_converter: GameConverter,
                 channel_provider: DiscordVoiceChannelProvider, participant_provider: ScrimParticipantProvider,
                 event_loop=None):
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
        channel_provider.client = self
        participant_provider.client = self

    def setup_logging(self):
        loggers = (logging.getLogger("discord"), logging.getLogger("sqlalchemy.engine"))
        for logger in loggers:
            logger.addHandler(self.logger.handler)
            logger.setLevel(logging.DEBUG)

    def setup_cogs(self):
        parent_path = Path(os.path.dirname(__file__)).parent
        for cog in os.listdir(os.path.join(parent_path, "Cogs")):
            if cog[-3:] == ".py" and not cog.startswith("_"):
                self.load_extension(f".{cog[:-3]}", package="Src.Bot.Cogs")

    def load_games(self):
        self.game_converter.init_games(self.config.games_dict)

    async def start_bot(self):
        print("Attempting a connection to Discord...")
        await self.start(self.config.token)

    async def get_prefix(self, message: discord.Message):
        guild_data = self.guild_converter.get_guild(message.guild.id)
        return guild_data.prefixes or self.config.default_prefix

    async def get_deletion_time(self, guild: discord.Guild) -> int:
        guild_data = await self.guild_converter.get_guild(guild.id)
        return guild_data.scrim_timeout or self.config.default_timeout

    async def get_context(self, message: discord.Message, *, cls=None) -> ScrimContext:
        return await self.context_provider.get_context(super(), message)

    async def invoke(self, ctx: Context):
        if ctx.command:
            await super().invoke(ctx)
        elif ctx.invoked_with:
            raise BotUnrecognizedCommandException(ctx)

    async def on_command_error(self, context: commands.Context, exception: Exception):
        if isinstance(exception, BotBaseContextException):
            await exception.resolve(context)

        elif isinstance(exception, BotBaseNoContextException):
            await exception.resolve()

        else:
            self.logger.critical(str(exception))
            raise exception

    async def on_ready(self):
        print(f"Successfully logged in as {self.user.name}, with version {__version__}")
        self.connected.set()


if __name__ == "__main__":  # pragma: no cover
    loop = asyncio.get_event_loop()
    client = ScrimBotClient()
    client.setup_logging()
    client.load_games()
    client.setup_cogs()
    loop.run_until_complete(client.start_bot())
