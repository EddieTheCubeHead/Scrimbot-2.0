__version__ = "0.1"
__author__ = "Eetu Asikainen"

from asyncio import wait, sleep
from typing import Optional
from unittest.mock import MagicMock

from behave import *
from behave.api.async_step import async_run_until_complete
from behave.runner import Context
from discord import Reaction, Message

from Bot.DataClasses.UserScrimResult import Result
from Test.AcceptanceTest.steps.mock_discord_objects_steps import create_voice_channels
from Bot.Converters.GameConverter import GameConverter
from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Test.Utils.TestHelpers.TestIdGenerator import GLOBAL_ID_GENERATOR
from Test.Utils.TestHelpers.embed_test_helper import parse_embed_from_table, create_error_embed, assert_same_embed_text
from Test.Utils.TestHelpers.ResponseLoggerContext import ResponseLoggerContext
from Test.Utils.TestHelpers.id_parser import process_inserts, get_id_increment, try_get_id
from Test.Utils.TestHelpers.test_utils import create_mock_guild, create_mock_author, create_mock_channel,\
    create_async_mock_message


def hide_command_calls(context: Context, amount: int) -> Optional[Message]:
    latest_fetched = None
    for _ in range(amount):
        latest_fetched = ResponseLoggerContext.get_oldest()
        context.command_messages.pop(-1)
    return latest_fetched


@given("channel registered for scrims")
@async_run_until_complete
async def step_impl(context: Context):
    table = _create_call_ids(context)
    await execute_command(';register', context, table)
    context.latest_fetched = hide_command_calls(context, 1)


@given("a {game} scrim")
@given("an {game} scrim")
@async_run_until_complete
async def step_impl(context: Context, game):
    await _create_scrim(context, game)


@given("a {game} scrim with {amount} players present")
@given("an {game} scrim with {amount} players present")
@async_run_until_complete
async def step_impl(context: Context, game, amount):
    await _create_scrim(context, game)
    if amount == "enough":
        game_instance = await BotDependencyInjector.dependencies[GameConverter].convert(MagicMock(), game)
        amount = game_instance.team_count * game_instance.min_team_size
    await _add_reactions(amount, context, "🎮")


@given("a {game} scrim in locked state")
@given("an {game} scrim in locked state")
@async_run_until_complete
async def step_impl(context: Context, game):
    await _create_locked_scrim(context, game)


async def _create_locked_scrim(context, game, amount=0):
    await _create_scrim(context, game, amount)
    game_instance = await BotDependencyInjector.dependencies[GameConverter].convert(MagicMock(), game)
    amount = game_instance.team_count * game_instance.min_team_size
    await _add_reactions(amount, context, "🎮", 1)
    await sleep(0)  # Discord.py queue system for events is dumb. This ensures all reactions are added
    table = _create_call_ids(context)
    await execute_command(";lock", context, table)
    context.command_messages.pop(-1)


@given("a {game} scrim with full teams and {amount} registered voice channels")
@given("an {game} scrim with full teams and {amount} registered voice channels")
@given("a {game} scrim with full teams and {amount} registered voice channel")
@given("an {game} scrim with full teams and {amount} registered voice channel")
@async_run_until_complete
async def step_impl(context: Context, game, amount):
    await create_filled_game(amount, context, game)


@given("a {game} scrim with full teams")
@given("an {game} scrim with full teams")
@async_run_until_complete
async def step_impl(context: Context, game):
    await create_filled_game(0, context, game)


@given("user {user} has a {game} rating of {value}")
@given("user {user} has an {game} rating of {value}")
@async_run_until_complete
async def step_impl(context, user: str, game: str, value: str):
    with context.mock_context_provider.as_admin():
        await call_command(context, f";rating {user} {game} {value}")
    hide_command_calls(context, 1)


@given("user {user} has prior {game} results")
@async_run_until_complete
async def step_impl(context, user: str, game: str):
    wins = int(context.table[0][0])
    losses = int(context.table[0][1])
    ties = int(context.table[0][2])
    unregistered = int(context.table[0][3])
    for _ in range(wins):
        await _create_scrim_result(context, game, Result.WIN)
    for _ in range(losses):
        await _create_scrim_result(context, game, Result.LOSS)
    for _ in range(ties):
        await _create_scrim_result(context, game, Result.TIE)
    for _ in range(unregistered):
        await _create_scrim_result(context, game, Result.UNREGISTERED)


async def _create_scrim_result(context: Context, game: str, result: Result):
    await create_filled_game(0, context, game)
    await call_command(context, ';start false')
    result_call = _get_result_command(result)
    await call_command(context, result_call)


def _get_result_command(result: Result):
    if result == Result.WIN:
        return ';winner 1'
    elif result == Result.LOSS:
        return ';winner 2'
    elif result == Result.TIE:
        return ';tie'
    return ';end'


async def create_filled_game(amount, context, game):
    await _create_locked_scrim(context, game, amount)
    await sleep(0)
    game_instance = await BotDependencyInjector.dependencies[GameConverter].convert(MagicMock(), game)
    max_team_players = game_instance.max_team_size
    team_count = game_instance.team_count
    for team in range(team_count):
        for user in range(1 + max_team_players * team, 1 + max_team_players + max_team_players * team):
            await add_user_reaction(context, _try_insert_number_react(f"{team + 1}\u20E3"), user)
    await sleep(0)


async def _create_scrim(context: Context, game, amount=0):
    table = _create_call_ids(context)
    await _ensure_registered_channel(context, table, amount)
    await execute_command(f';scrim "{game}"', context, table)
    context.latest_fetched = hide_command_calls(context, 1)


async def _ensure_registered_channel(context: Context, table, amount: int = 0):
    if not context.scrim_channel_registered:
        await _register_channel(context, table, amount)
        context.scrim_channel_registered = True


async def _register_channel(context: Context, table, amount: int = 0):
    register_command = ";register"
    if amount:
        create_voice_channels(context, amount, lobby=True)
        register_command += " {voice_"
        register_command += "_id} {voice_".join(str(num) for num in range(1, int(amount) + 1))
        register_command += "_id}"
        register_command += " l:{voice_0_id}"
        register_command = process_inserts(context, register_command)
    await execute_command(register_command, context, table)
    context.latest_fetched = hide_command_calls(context, 1)


@when("{command} is called")
@async_run_until_complete
async def step_impl(context: Context, command: str):
    await call_command(context, command)


@when("{command} is called from another channel")
@async_run_until_complete
async def step_impl(context: Context, command: str):
    await call_command(context, command, True)


async def call_command(context: Context, command: str, alternative_text_channel: bool = False):
    table = _create_call_ids(context, alternative_text_channel=alternative_text_channel)
    command = process_inserts(context, command)
    context.latest_command = command.split(" ")[0][1:]
    context.latest_prefix = command[0]
    await execute_command(command, context, table)


def _create_call_ids(context: Context, *, alternative_text_channel=False) -> list[list[str]]:
    channel_id = try_get_id(context, "channel_id" if not alternative_text_channel else "text_2_id")
    guild_id = try_get_id(context, "guild_id")
    user_id = try_get_id(context, "user_id")
    return [[user_id, channel_id, guild_id]]


async def execute_command(command, context: Context, table):
    for row in table:
        mock_guild = create_mock_guild(int(row[2]))
        mock_author = create_mock_author(int(row[0]), mock_guild, context)
        mock_channel = create_mock_channel(int(row[1]), mock_guild)
        mock_message = create_async_mock_message(mock_guild, mock_channel, mock_author, command)
        context.patcher.try_add_group(mock_channel)
        context.command_messages.append(mock_message)
        with context.patcher.patch_all():
            await context.client.on_message(mock_message)


@when("a user reacts with {reaction_string}")
@async_run_until_complete
async def step_impl(context: Context, reaction_string):
    await _add_reactions(1, context, reaction_string)


@when("user {user} reacts with {reaction_string}")
@async_run_until_complete
async def step_impl(context: Context, user, reaction_string):
    await add_user_reaction(context, _try_insert_number_react(reaction_string), user)


async def add_user_reaction(context, reaction_string, user):
    user_id = try_get_id(context, f"user_{user}_id")
    guild = create_mock_guild(try_get_id(context, "guild_id"))
    user = create_mock_author(user_id, guild, context)
    reaction = Reaction(data={}, message=context.latest_fetched, emoji=reaction_string)
    await context.latest_fetched.add_reaction(reaction_string, user)
    context.client.dispatch("reaction_add", reaction, user)


@when("users {users_string} react with {reaction_string}")
@async_run_until_complete
async def step_impl(context: Context, users_string, reaction_string):
    for user in _parse_users(users_string):
        await add_user_reaction(context, _try_insert_number_react(reaction_string), user)


def _parse_users(users_string):
    if "to" in users_string:
        return list(range(int(users_string[0]), int(users_string[-1]) + 1))
    return [int(c) for c in users_string if c.isdigit()]


def _try_insert_number_react(reaction_string):
    number_mappings = {
        "1️⃣": "1\u20E3",
        "2️⃣": "2\u20E3"
    }
    if reaction_string in number_mappings:
        return number_mappings[reaction_string]
    return reaction_string


@when("{amount} users react with {reaction_string}")
@async_run_until_complete
async def step_impl(context: Context, amount, reaction_string):
    await _add_reactions(amount, context, _try_insert_number_react(reaction_string))


async def _add_reactions(amount, context: Context, reaction_string, increment_start=None):
    guild = create_mock_guild(try_get_id(context, "guild_id"))
    user_increment = get_id_increment(context, "user") if increment_start is None else increment_start
    for increment in range(user_increment, user_increment + int(amount)):
        await _add_reaction(context, guild, reaction_string, increment)


async def _add_reaction(context: Context, guild, reaction_string, user_increment):
    user_id = try_get_id(context, f"user_{user_increment}_id")
    user = create_mock_author(user_id, guild, context)
    context.discord_ids[f"user_{user_increment}_id"] = user.id
    reaction = Reaction(data={}, message=context.latest_fetched, emoji=reaction_string)
    await context.latest_fetched.add_reaction(reaction_string, user)
    context.client.dispatch("reaction_add", reaction, user)


@when("user {user} removes reaction {reaction_string}")
@async_run_until_complete
async def step_impl(context: Context, user, reaction_string):
    guild = create_mock_guild(try_get_id(context, "guild_id"))
    user_id = try_get_id(context, f"user_{user}_id")
    await _remove_reaction(context, guild, _try_insert_number_react(reaction_string), user_id)


async def _remove_reaction(context: Context, guild, reaction_string, user_id):
    user = create_mock_author(user_id, guild, context)
    reaction = Reaction(data={}, message=context.latest_fetched, emoji=reaction_string)
    await context.latest_fetched.remove_reaction(reaction_string, user)
    context.client.dispatch("reaction_remove", reaction, user)


@when("the task to prune waiting scrims is ran")
@async_run_until_complete
async def step_impl(context):
    with context.patcher.patch_all():
        await context.client.cogs['VoiceJoinListener'].prune_observers()
        await sleep(0)


@then("command message is deleted")
@then("command messages are deleted")
def step_impl(context: Context):
    for message in context.command_messages:
        message.delete.assert_called()


@then("embed received with fields")
@async_run_until_complete
async def step_impl(context: Context):
    embed = parse_embed_from_table(context)
    context.latest_fetched = ResponseLoggerContext.get_oldest()
    assert_same_embed_text(context, embed, context.latest_fetched.embeds[0])


@then("error received with message")
def step_impl(context: Context):
    error_message = context.text.strip()
    embed = create_error_embed(error_message, context.latest_command, context)
    context.latest_fetched = ResponseLoggerContext.get_oldest()
    assert_same_embed_text(context, embed, context.latest_fetched.embeds[0])


@then("error and help received with message")
def step_impl(context: Context):
    error_message = context.text.strip()
    embed = create_error_embed(error_message, context.latest_command, context,
                               f"{context.latest_prefix}help {context.latest_command}")
    context.latest_fetched = ResponseLoggerContext.get_oldest()
    assert_same_embed_text(context, embed, context.latest_fetched.embeds[0])


@then("team joining emojis reacted by bot")
def step_impl(context: Context):
    message = context.latest_fetched
    assert "\U0001F3AE" in [reaction.emoji for reaction in message.reactions]
    assert "\U0001F441" in [reaction.emoji for reaction in message.reactions]


@then("embed edited to have fields")
def step_impl(context: Context):
    embed = parse_embed_from_table(context)
    assert_same_embed_text(context, embed, context.latest_fetched.embeds[0])


@then("scrim message has reactions")
def step_impl(context: Context):
    message = context.latest_fetched
    allowed_reactions = []
    for reaction, amount in context.table:
        allowed_reactions.append(_try_insert_number_react(reaction))
        actual_count = message.raw_reactions.count(_try_insert_number_react(reaction))
        assert int(amount) == actual_count, f"Expected {amount} '{reaction}' reactions, but found {actual_count}."
    for message_reaction in message.raw_reactions:
        assert message_reaction in allowed_reactions, f"Did not expect the message to have the reaction" \
                                                      f"'{message_reaction}'"


@then("scrim message has no reactions")
def step_impl(context: Context):
    message = context.latest_fetched
    assert len(message.raw_reactions) == 0, f"Expected the message to have no reactions, but found the following" \
                                            f"reaction(s): {message.raw_reactions}"


@then("error message deleted after {seconds} seconds")
def step_impl(context: Context, seconds):
    assert context.latest_fetched.deletion_time == float(seconds), f"Expected deletion time to be {seconds} seconds, " \
                                                                   f"but it was {context.latest_fetched.deletion_time}."
