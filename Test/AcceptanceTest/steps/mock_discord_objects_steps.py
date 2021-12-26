__version__ = "0.1"
__author__ = "Eetu Asikainen"

from behave import *

from Utils.TestHelpers.MockDiscordConverter import MockDiscordConverter
from Utils.TestHelpers.TestIdGenerator import GLOBAL_ID_GENERATOR
from Utils.TestHelpers.test_utils import create_mock_channel, create_mock_guild, create_mock_channel_group


@given("exists {amount} voice channels")
def step_impl(context, amount):
    mock_voice_converter = MockDiscordConverter()
    context.patcher.add_patch("discord.ext.commands.converter.VoiceChannelConverter", mock_voice_converter)
    mock_guild = create_mock_guild(context.discord_ids.pop("guild_id", GLOBAL_ID_GENERATOR.generate_viable_id()))
    context.discord_ids["guild_id"] = mock_guild.id
    channel_increment = 1
    while f"voice_{channel_increment}_id" in context.discord_ids:
        channel_increment += 1
    for _ in range(int(amount)):
        mocked_channel = create_mock_channel(GLOBAL_ID_GENERATOR.generate_viable_id(), mock_guild)
        name_matches = _create_voice_channel_conversion_matches(str(mocked_channel.id))
        mock_voice_converter.add_mock_call(name_matches, mocked_channel, (["guild", "id"], mock_guild.id))
        context.discord_ids[f"voice_{channel_increment}_id"] = mocked_channel.id
        channel_increment += 1


@given("exists channel group")
def step_impl(context):
    mock_voice_converter = MockDiscordConverter()
    context.patcher.add_patch("discord.ext.commands.converter.VoiceChannelConverter", mock_voice_converter)
    mock_guild = create_mock_guild(context.discord_ids.pop("guild_id", GLOBAL_ID_GENERATOR.generate_viable_id()))
    context.discord_ids["guild_id"] = mock_guild.id
    mock_group = create_mock_channel_group(GLOBAL_ID_GENERATOR.generate_viable_id(), mock_guild)
    context.patcher.add_channel_group(mock_group)
    channel_increment = 1
    while f"voice_{channel_increment}_id" in context.discord_ids:
        channel_increment += 1
    for row in context.table:
        mocked_channel = create_mock_channel(GLOBAL_ID_GENERATOR.generate_viable_id(), mock_guild)
        mocked_channel.name = row[1]
        mocked_channel.category = mock_group
        mocked_channel.category_id = mock_group.id
        name_matches = _create_voice_channel_conversion_matches(mocked_channel.name)
        if row[0] == "voice":
            mock_group.voice_channels.append(mocked_channel)
            mock_voice_converter.add_mock_call(name_matches, mocked_channel, (["guild", "id"], mock_guild.id))
            context.discord_ids[f"voice_{channel_increment}_id"] = mocked_channel.id
            channel_increment += 1
        elif row[0] == "text":
            mock_group.text_channels.append(mocked_channel)
            context.discord_ids["channel_id"] = mocked_channel.id


def _create_voice_channel_conversion_matches(channel_name_id: str) -> list[str]:
    return [f"<#{channel_name_id}>", channel_name_id]
