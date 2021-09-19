__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from behave import *

from Utils.TestHelpers.MockDiscordConverter import MockDiscordConverter
from Utils.TestHelpers.test_utils import create_mock_channel, create_mock_guild


@given("exists discord voice channels")
def step_impl(context):
    mock_voice_converter = MockDiscordConverter()
    context.patcher.add_patch("discord.ext.commands.converter.VoiceChannelConverter", mock_voice_converter)
    mock_guilds = {}
    for row in context.table:
        if row[0] in mock_guilds:
            mock_guild = mock_guilds[row[0]]
        else:
            mock_guild = create_mock_guild(int(row[0]))
            mock_guilds[row[0]] = mock_guild
        mocked_channel = create_mock_channel(int(row[1]), mock_guild)
        name_matches = _create_voice_channel_conversion_matches(row[1])
        mock_voice_converter.add_mock_call(name_matches, mocked_channel, (["guild", "id"], mock_guild.id))


def _create_voice_channel_conversion_matches(channel_name_id: str) -> list[str]:
    return [f"<#{channel_name_id}>", channel_name_id]
