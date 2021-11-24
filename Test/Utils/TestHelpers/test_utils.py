__version__ = "0.1"
__author__ = "Eetu Asikainen"

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Tuple, Type, Optional
from unittest.mock import MagicMock, AsyncMock

import discord

from Bot.Core.ScrimContext import ScrimContext
from Bot import Cogs
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


_ID_GENERATOR = TestIdGenerator()


def assert_tuple_with_correct_types(actual: Tuple, *tuple_fields: Type) -> Optional[str]:
    if len(actual) != len(tuple_fields):
        return f"Expected a tuple with length of {len(tuple_fields)}, actual length was {len(actual)}!"
    for actual, expected in zip(actual, tuple_fields):
        if not isinstance(actual, expected):
            return f"Expected an instance of {expected}, got an instance of {type(actual)}."


def get_cogs_messages():
    for cog in os.listdir(os.path.dirname(Cogs.__file__)):
        if re.match(r"^[^_][a-zA-Z]*\.py$", cog):
            yield rf"Using cog Bot.Cogs.{cog[:-3]}, with version {__version__}"


def create_mock_author(member_id: int, guild: discord.Guild) -> discord.Member:
    mock_member = MagicMock()
    mock_member.id = member_id
    mock_member.guild = guild
    mock_member.display_name = f"User{member_id}"
    mock_member.bot = False
    return mock_member


def create_mock_channel(channel_id: int, guild: discord.Guild) -> discord.TextChannel:
    mock_channel = MagicMock()
    mock_channel.id = channel_id
    mock_channel.name = str(channel_id)
    mock_channel.guild = guild
    return mock_channel


def create_mock_channel_group(group_id: int, guild: discord.Guild) -> discord.CategoryChannel:
    mock_channel_group = MagicMock()
    mock_channel_group.id = group_id
    mock_channel_group.name = str(group_id)
    mock_channel_group.guild = guild
    mock_channel_group.voice_channels = []
    mock_channel_group.text_channels = []
    return mock_channel_group


def create_mock_guild(guild_id: int) -> discord.Guild:
    mock_guild = MagicMock()
    mock_guild.id = guild_id
    return mock_guild


def create_mock_message(guild: discord.Guild, channel: discord.TextChannel, author: discord.Member, message: str) \
        -> discord.Message:
    mock_message = MagicMock()
    _populate_message(author, channel, guild, message, mock_message)
    return mock_message


def _populate_message(author, channel, guild, message, mock_message):
    mock_message.id = _ID_GENERATOR.generate_viable_id()
    mock_message.guild = guild
    mock_message.channel = channel
    mock_message.content = message
    mock_message.author = author
    mock_message.created_at = datetime.now()


def create_async_mock_message(guild: discord.Guild, channel: discord.TextChannel, author: discord.Member,
                              message: str) -> discord.Message:
    mock_message = AsyncMock()
    _populate_message(author, channel, guild, message, mock_message)
    return mock_message


def _create_mock_bot():
    mock_bot = AsyncMock()
    mock_bot.can_run = AsyncMock(return_value=True)
    return mock_bot


def create_mock_context(guild_id: int, channel_id: int, author_id: int,
                        message: str) -> ScrimContext:
    mock_context = MagicMock(spec=ScrimContext)
    mock_context.guild = create_mock_guild(guild_id)
    mock_context.channel = create_mock_channel(channel_id, mock_context.guild)
    mock_context.author = create_mock_author(author_id, mock_context.guild)
    mock_context.message = create_mock_message(mock_context.guild, mock_context.channel, mock_context.author, message)
    mock_context.bot = _create_mock_bot()
    mock_context.send = AsyncMock()
    return mock_context
