__version__ = "0.1"
__author__ = "Eetu Asikainen"

import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Tuple, Type, Optional, Union
from unittest.mock import MagicMock, AsyncMock

import discord

from Bot.Core.ScrimContext import ScrimContext
from Test.Utils.TestHelpers.TestIdGenerator import TestIdGenerator


_ID_GENERATOR = TestIdGenerator()


class _VoicePresenceSentinel:

    def __init__(self, present: bool = True):
        self.present = present


def assert_tuple_with_correct_types(actual: Tuple, *tuple_fields: Type) -> Optional[str]:
    if len(actual) != len(tuple_fields):
        return f"Expected a tuple with length of {len(tuple_fields)}, actual length was {len(actual)}!"
    for actual, expected in zip(actual, tuple_fields):
        if not isinstance(actual, expected):
            return f"Expected an instance of {expected}, got an instance of {type(actual)}."


def assert_almost_now(timestamp: datetime, delta: timedelta = timedelta(milliseconds=200)):
    now = datetime.now()
    assert now - timestamp < delta,\
        f"Expected timestamp {timestamp} to be within delta {timedelta} of current time {now}"


def get_cogs_messages():
    from Bot import Cogs
    for cog in os.listdir(os.path.dirname(Cogs.__file__)):
        if re.match(r"^[^_][a-zA-Z]*\.py$", cog):
            yield rf"Using cog Bot.Cogs.{cog[:-3]}, with version {__version__}"


def set_member_voice_present(context, member_id: int, guild: discord.Guild):
    if (member_id, guild.id) in context.mocked_users:
        if type(context.mocked_users[(member_id, guild.id)]) == _VoicePresenceSentinel:
            context.mocked_users[(member_id, guild.id)] = _VoicePresenceSentinel()
            return
        mock_voice = MagicMock()
        mock_voice.channel.guild = guild
        context.mocked_users[(member_id, guild.id)].voice = mock_voice
    else:
        context.mocked_users[(member_id, guild.id)] = _VoicePresenceSentinel()


def set_member_voice_not_present(context, member_id: int, guild: discord.Guild):
    if (member_id, guild.id) in context.mocked_users:
        context.mocked_users[(member_id, guild.id)].voice = None
    else:
        context.mocked_users[(member_id, guild.id)] = _VoicePresenceSentinel(False)


def create_mock_author(member_id: int, guild: discord.Guild, context=None) -> discord.Member:
    in_voice = False
    if context and (member_id, guild.id) in context.mocked_users:
        if type(context.mocked_users[(member_id, guild.id)]) == _VoicePresenceSentinel:
            in_voice = context.mocked_users[(member_id, guild.id)].present
        else:
            return context.mocked_users[(member_id, guild.id)]
    mock_member = AsyncMock()
    mock_member.move_to = AsyncMock()
    mock_member.id = member_id
    mock_member.guild = guild
    mock_member.display_name = f"User{member_id}"
    mock_member.bot = False
    if in_voice:
        mock_member.voice.channel.guild = guild
    if context:
        context.mocked_users[(member_id, guild.id)] = mock_member
    return mock_member


def create_mock_channel(channel_id: int, guild: discord.Guild) -> discord.TextChannel:
    mock_channel = AsyncMock()
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


def create_team_from_ratings(*ratings: int):
    team_members = []
    for rating in ratings:
        team_members.append(_create_user_rating(rating))
    return team_members


def _create_user_rating(rating: int):
    mock_rating = MagicMock()
    mock_rating.rating = rating
    return mock_rating


def create_mock_strategy(strategy_name: str):
    mock_strategy = MagicMock()
    mock_strategy.name = strategy_name
    return mock_strategy
