__version__ = "0.1"
__author__ = "Eetu Asikainen"

from behave import *

from Utils.TestHelpers.MockDiscordConverter import MockDiscordConverter
from Utils.TestHelpers.test_utils import create_mock_channel, create_mock_guild, create_mock_channel_group


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


@given("exists channel group '{group_id}' in guild '{guild_id}'")
def step_impl(context, group_id, guild_id):
    mock_voice_converter = MockDiscordConverter()
    context.patcher.add_patch("discord.ext.commands.converter.VoiceChannelConverter", mock_voice_converter)
    mock_guild = create_mock_guild(int(guild_id))
    mock_group = create_mock_channel_group(group_id, mock_guild)
    context.patcher.add_channel_group(mock_group)
    for row in context.table:
        mocked_channel = create_mock_channel(int(row[2]), mock_guild)
        mocked_channel.name = row[1]
        mocked_channel.category = mock_group
        mocked_channel.category_id = mock_group.id
        name_matches = _create_voice_channel_conversion_matches(mocked_channel.name)
        if row[0] == "voice":
            mock_group.voice_channels.append(mocked_channel)
        elif row[0] == "text":
            mock_group.text_channels.append(mocked_channel)
        mock_voice_converter.add_mock_call(name_matches, mocked_channel, (["guild", "id"], mock_guild.id))


def _create_voice_channel_conversion_matches(channel_name_id: str) -> list[str]:
    return [f"<#{channel_name_id}>", channel_name_id]
