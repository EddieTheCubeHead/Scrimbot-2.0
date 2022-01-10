__version__ = "0.1"
__author__ = "Eetu Asikainen"

from behave import *
from behave.runner import Context

from Test.Utils.TestHelpers.MockDiscordConverter import MockDiscordConverter
from Test.Utils.TestHelpers.TestIdGenerator import GLOBAL_ID_GENERATOR
from Test.Utils.TestHelpers.id_parser import get_id_increment, try_get_id
from Test.Utils.TestHelpers.test_utils import create_mock_channel, create_mock_guild, create_mock_channel_group


@given("exists {amount} voice channels")
def step_impl(context, amount):
    mock_voice_converter = _create_mock_voice_converter(context)
    mock_guild = _ensure_mocked_guild(context)
    channel_increment = get_id_increment(context, "channel")
    for increment in range(channel_increment, channel_increment + int(amount)):
        _create_channel(increment, context, mock_guild, mock_voice_converter)


@given("exists channel group")
def step_impl(context):
    mock_voice_converter = _create_mock_voice_converter(context)
    mock_guild = _ensure_mocked_guild(context)
    mock_group = _create_mock_group(context, mock_guild)
    channel_increment = get_id_increment(context, "channel")
    for row in context.table:
        mocked_channel = _insert_mock_channel_data(mock_group, mock_guild, row)
        if row[0] == "voice":
            _mock_voice_channel_calls(channel_increment, context, mock_group, mock_guild, mock_voice_converter,
                                      mocked_channel)
            channel_increment += 1
        elif row[0] == "text":
            _mock_text_channel_calls(context, mock_group, mocked_channel)


def _mock_voice_presence(player):
    pass


@given("{player_spec} in voice chat")
def step_impl(context: Context, player_spec):
    players = _parse_player_spec(player_spec)
    for player in players:
        _mock_voice_presence(player)
    
    
def _parse_player_spec(player_spec):
    if "all" in player_spec:
        return []
    player_spec = player_spec.remove("players ")
    if "to" in player_spec:
        return list(range(int(player_spec[0]), int(player_spec[-1]) + 1))
    return [int(c) for c in player_spec if c.isdigit()]


def _create_mock_voice_converter(context):
    mock_voice_converter = MockDiscordConverter()
    context.patcher.add_patch("discord.ext.commands.converter.VoiceChannelConverter", mock_voice_converter)
    return mock_voice_converter


def _create_mock_group(context, mock_guild):
    mock_group = create_mock_channel_group(GLOBAL_ID_GENERATOR.generate_viable_id(), mock_guild)
    context.patcher.add_channel_group(mock_group)
    return mock_group


def _ensure_mocked_guild(context):
    mock_guild_id = try_get_id(context, "guild_id")
    mock_guild = create_mock_guild(mock_guild_id)
    return mock_guild


def _create_channel(channel_increment, context, mock_guild, mock_voice_converter):
    mocked_channel = create_mock_channel(GLOBAL_ID_GENERATOR.generate_viable_id(), mock_guild)
    name_matches = _create_voice_channel_conversion_matches(str(mocked_channel.id))
    mock_voice_converter.add_mock_call(name_matches, mocked_channel, (["guild", "id"], mock_guild.id))
    context.discord_ids[f"voice_{channel_increment}_id"] = mocked_channel.id


def _insert_mock_channel_data(mock_group, mock_guild, row):
    mocked_channel = create_mock_channel(GLOBAL_ID_GENERATOR.generate_viable_id(), mock_guild)
    mocked_channel.name = row[1]
    mocked_channel.category = mock_group
    mocked_channel.category_id = mock_group.id
    return mocked_channel


def _mock_voice_channel_calls(channel_increment, context, mock_group, mock_guild, mock_voice_converter, mocked_channel):
    mock_group.voice_channels.append(mocked_channel)
    name_matches = _create_voice_channel_conversion_matches(mocked_channel.name)
    mock_voice_converter.add_mock_call(name_matches, mocked_channel, (["guild", "id"], mock_guild.id))
    context.discord_ids[f"voice_{channel_increment}_id"] = mocked_channel.id


def _create_voice_channel_conversion_matches(channel_name_id: str) -> list[str]:
    return [f"<#{channel_name_id}>", channel_name_id]


def _mock_text_channel_calls(context, mock_group, mocked_channel):
    mock_group.text_channels.append(mocked_channel)
    context.discord_ids["channel_id"] = mocked_channel.id
