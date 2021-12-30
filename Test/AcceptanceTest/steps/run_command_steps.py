__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from behave import *
from behave.api.async_step import async_run_until_complete
from discord import Reaction

from Bot.Converters.GameConverter import GameConverter
from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Utils.TestHelpers.TestIdGenerator import GLOBAL_ID_GENERATOR
from Utils.TestHelpers.embed_test_helper import parse_embed_from_table, create_error_embed, assert_same_embed_text
from Bot.DataClasses.ScrimChannel import ScrimChannel
from Utils.TestHelpers.ResponseLoggerContext import ResponseLoggerContext
from Utils.TestHelpers.id_parser import insert_ids, get_id_increment, try_get_id
from Utils.TestHelpers.test_utils import create_mock_guild, create_mock_author, create_mock_channel,\
    create_async_mock_message


@given("channel registered for scrims")
@async_run_until_complete
async def step_impl(context):
    table = _create_call_ids(context)
    await call_command(';register', context, table)
    ResponseLoggerContext.get_oldest()


@given("a {game} scrim")
@given("an {game} scrim")
@async_run_until_complete
async def step_impl(context, game):
    await _create_scrim(context, game)


@given("a {game} scrim with {amount} players present")
@given("an {game} scrim with {amount} players present")
@async_run_until_complete
async def step_impl(context, game, amount):
    await _create_scrim(context, game)
    if amount == "enough":
        game_instance = await BotDependencyInjector.dependencies[GameConverter].convert(MagicMock(), game)
        amount = game_instance.team_count * game_instance.min_team_size
    await _add_reactions(amount, context, "🎮")


async def _create_scrim(context, game):
    table = _create_call_ids(context)
    await call_command(';register', context, table)
    await call_command(f';scrim "{game}"', context, table)
    ResponseLoggerContext.get_oldest()
    context.latest_fetched = ResponseLoggerContext.get_oldest()


@when("{command} is called")
@async_run_until_complete
async def step_impl(context, command: str):
    command = insert_ids(context, command)
    context.latest_command = command.split(" ")[0][1:]
    context.latest_prefix = command[0]
    table = _create_call_ids(context)
    await call_command(command, context, table)


@when("{command} is called from another channel")
@async_run_until_complete
async def step_impl(context, command: str):
    command = insert_ids(context, command)
    context.latest_command = command.split(" ")[0][1:]
    context.latest_prefix = command[0]
    table = _create_call_ids(context, alternative_text_channel=True)
    await call_command(command, context, table)


def _create_call_ids(context, *, alternative_text_channel=False) -> list[list[str]]:
    channel_id = try_get_id(context, "channel_id" if not alternative_text_channel else "text_2_id")
    guild_id = try_get_id(context, "guild_id")
    user_id = try_get_id(context, "user_id")
    return [[user_id, channel_id, guild_id]]


async def call_command(command, context, table):
    for row in table:
        mock_guild = create_mock_guild(int(row[2]))
        mock_author = create_mock_author(int(row[0]), mock_guild)
        mock_channel = create_mock_channel(int(row[1]), mock_guild)
        mock_message = create_async_mock_message(mock_guild, mock_channel, mock_author, command)
        context.patcher.try_add_group(mock_channel)
        with context.patcher.patch_all():
            await context.client.on_message(mock_message)


@then("embed received with fields")
@async_run_until_complete
async def step_impl(context):
    embed = parse_embed_from_table(context)
    context.latest_fetched = ResponseLoggerContext.get_oldest()
    assert_same_embed_text(embed, context.latest_fetched.embeds[0])


@then("error received with message")
def step_impl(context):
    error_message = context.text.strip()
    embed = create_error_embed(error_message, context.latest_command, context)
    context.latest_fetched = ResponseLoggerContext.get_oldest()
    assert_same_embed_text(embed, context.latest_fetched.embeds[0])


@then("error and help received with message")
def step_impl(context):
    error_message = context.text.strip()
    embed = create_error_embed(error_message, context.latest_command, context,
                               f"{context.latest_prefix}help {context.latest_command}")
    context.latest_fetched = ResponseLoggerContext.get_oldest()
    assert_same_embed_text(embed, context.latest_fetched.embeds[0])


@then("team joining emojis reacted by bot")
def step_impl(context):
    message = context.latest_fetched
    assert "\U0001F3AE" in message.test_reactions
    assert "\U0001F441" in message.test_reactions


@when("a user reacts with {reaction_string}")
@async_run_until_complete
async def step_impl(context, reaction_string):
    await _add_reactions(1, context, reaction_string)


@when("user {user} reacts with {reaction_string}")
@async_run_until_complete
async def step_impl(context, user, reaction_string):
    user_id = try_get_id(context, f"user_{user}_id")
    guild = create_mock_guild(try_get_id(context, "guild_id"))
    user = create_mock_author(user_id, guild)
    reaction = Reaction(data={}, message=context.latest_fetched, emoji=reaction_string)
    await context.latest_fetched.add_reaction(reaction_string)
    context.client.dispatch("reaction_add", reaction, user)


@when("{amount} users react with {reaction_string}")
@async_run_until_complete
async def step_impl(context, amount, reaction_string):
    await _add_reactions(amount, context, reaction_string)


async def _add_reactions(amount, context, reaction_string):
    guild = create_mock_guild(try_get_id(context, "guild_id"))
    user_increment = get_id_increment(context, "user")
    for increment in range(user_increment, user_increment + int(amount)):
        await _add_reaction(context, guild, reaction_string, increment)


async def _add_reaction(context, guild, reaction_string, user_increment):
    user = create_mock_author(GLOBAL_ID_GENERATOR.generate_viable_id(), guild)
    context.discord_ids[f"user_{user_increment}_id"] = user.id
    reaction = Reaction(data={}, message=context.latest_fetched, emoji=reaction_string)
    await context.latest_fetched.add_reaction(reaction_string)
    context.client.dispatch("reaction_add", reaction, user)


@when("user {user} removes reaction {reaction_string}")
@async_run_until_complete
async def step_impl(context, user, reaction_string):
    guild = create_mock_guild(try_get_id(context, "guild_id"))
    user_id = try_get_id(context, f"user_{user}_id")
    await _remove_reaction(context, guild, reaction_string, user_id)


async def _remove_reaction(context, guild, reaction_string, user_id):
    user = create_mock_author(user_id, guild)
    reaction = Reaction(data={}, message=context.latest_fetched, emoji=reaction_string)
    await context.latest_fetched.remove_reaction(reaction_string, user)
    context.client.dispatch("reaction_remove", reaction, user)


@then("embed edited to have fields")
def step_impl(context):
    embed = parse_embed_from_table(context)
    assert_same_embed_text(embed, context.latest_fetched.embeds[0])


@then("scrim message has reactions")
def step_impl(context):
    message = context.latest_fetched
    for reaction, amount in context.table:
        actual_count = message.test_reactions.count(reaction)
        assert int(amount) == actual_count, f"Expected {amount} '{reaction}' reactions, but found {actual_count}."
