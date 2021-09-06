__version__ = "0.1"
__author__ = "Eetu Asikainen"

import datetime
from unittest.mock import MagicMock

import discord

from Bot.Core.ScrimContext import ScrimContext
from Utils.TestIdGenerator import TestIdGenerator

_ID_GENERATOR = TestIdGenerator()


def create_mock_author(member_id: str, guild: discord.Guild) -> discord.Member:
    mock_member = MagicMock()
    mock_member.id = int(member_id)
    mock_member.guild = guild
    mock_member.display_name = f"User{member_id}"
    return mock_member


def create_mock_channel(channel_id: str, guild: discord.Guild) -> discord.TextChannel:
    mock_channel = MagicMock()
    mock_channel.id = int(channel_id)
    mock_channel.guild = guild
    return mock_channel


def create_mock_guild(guild_id: str) -> discord.Guild:
    mock_guild = MagicMock()
    mock_guild.id = int(guild_id)
    return mock_guild


def create_mock_message(guild: discord.Guild, channel: discord.TextChannel, author: discord.Member, message: str) \
        -> discord.Message:
    mock_message = MagicMock()
    mock_message.id = _ID_GENERATOR.generate_viable_id()
    mock_message.guild = guild
    mock_message.channel = channel
    mock_message.content = message
    mock_message.author = author
    mock_message.created_at = datetime.datetime.now()
    return mock_message


def create_mock_context(guild: discord.Guild, channel: discord.TextChannel, author: discord.Member,
                        message: discord.Message) -> ScrimContext:
    mock_context = MagicMock(spec=ScrimContext)
    mock_context.guild = guild
    mock_context.channel = channel
    mock_context.author = author
    mock_context.message = message
    return mock_context
