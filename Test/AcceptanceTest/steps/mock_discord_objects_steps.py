__version__ = "0.1"
__author__ = "Eetu Asikainen"

import re

from behave import *
from behave.runner import Context
from discord import VoiceChannel

from Test.Utils.TestHelpers.MockDiscordConverter import MockDiscordConverter
from Test.Utils.TestHelpers.TestIdGenerator import GLOBAL_ID_GENERATOR
from Test.Utils.TestHelpers.id_parser import get_id_increment, try_get_id
from Test.Utils.TestHelpers.test_utils import create_mock_channel, create_mock_guild, create_mock_channel_group, \
    set_member_voice_present
from Test.Utils.TestHelpers.VoiceChannelFetchPatcher import VoiceChannelFetchPatcher


@given("exists {amount} voice channels")
def step_impl(context, amount):
    create_voice_channels(context, amount)


def create_voice_channels(context: Context, amount: int):
    mock_voice_converter = _create_mock_voice_converter(context)
    voice_fetch_patcher = _create_voice_fetch_patcher(context)
    mock_guild = _ensure_mocked_guild(context)
    channel_increment = get_id_increment(context, "channel")
    for increment in range(channel_increment, channel_increment + int(amount)):
        _create_channel(increment, context, mock_guild, mock_voice_converter, voice_fetch_patcher)


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


def _get_all_players(context):
    return [int(context.discord_ids[name]) for name in context.discord_ids if re.match(r"user_(\d+_|)id", name)]


@when("{player_spec} are in voice chat")
@when("{player_spec} is in voice chat")
def step_impl(context: Context, player_spec):
    players = _parse_player_spec(player_spec) or _get_all_players(context)
    guild = _ensure_mocked_guild(context)
    for player in players:
        set_member_voice_present(context, player, guild)
    
    
def _parse_player_spec(player_spec) -> list[int]:
    if "all" in player_spec:
        return []
    player_spec = player_spec.replace("players ", "")
    if "to" in player_spec:
        start, stop = player_spec.split(" to ")
        return list(range(int(start), int(stop) + 1))
    player_spec.replace(" and", ", ")
    return [int(num) for num in player_spec.split(", ") if num.isdigit()]


@then("{player_spec} moved to team {team_num} voice channel")
def step_impl(context: Context, player_spec, team_num):
    players = _parse_player_spec(player_spec) or _get_all_players(context)
    guild = _ensure_mocked_guild(context)
    for player in players:
        player_id = try_get_id(context, f"user_{player}_id")
        channel: VoiceChannel = context.mocked_users[(player_id, guild.id)].move_to.call_args[0][0]
        channel_id = str(try_get_id(context, f"voice_{team_num}_id"))
        assert channel.name == channel_id, f"Expected channel name to be {channel_id} but it was {channel.name}."


@then("no players moved")
def step_impl(context: Context):
    guild = _ensure_mocked_guild(context)
    for player in _get_all_players(context):
        player_id = try_get_id(context, f"user_{player}_id")
        if (player_id, guild.id) in context.mocked_users:
            context.mocked_users[(player_id, guild.id)].move_to.assert_not_called()


def _create_mock_voice_converter(context):
    mock_voice_converter = MockDiscordConverter()
    context.patcher.add_patch("discord.ext.commands.converter.VoiceChannelConverter", mock_voice_converter)
    return mock_voice_converter


def _create_voice_fetch_patcher(context):
    voice_fetch_patcher = VoiceChannelFetchPatcher()
    context.patcher.add_patch("discord.client.Client.get_channel", voice_fetch_patcher)
    return voice_fetch_patcher


def _create_mock_group(context, mock_guild):
    mock_group = create_mock_channel_group(GLOBAL_ID_GENERATOR.generate_viable_id(), mock_guild)
    context.patcher.add_channel_group(mock_group)
    return mock_group


def _ensure_mocked_guild(context):
    mock_guild_id = try_get_id(context, "guild_id")
    mock_guild = create_mock_guild(mock_guild_id)
    return mock_guild


def _create_channel(channel_increment, context, mock_guild, mock_voice_converter, voice_fetch_patcher):
    mocked_channel = create_mock_channel(GLOBAL_ID_GENERATOR.generate_viable_id(), mock_guild)
    name_matches = _create_voice_channel_conversion_matches(str(mocked_channel.id))
    mock_voice_converter.add_mock_call(name_matches, mocked_channel, (["guild", "id"], mock_guild.id))
    voice_fetch_patcher.add_mocked_channel(mocked_channel)
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
