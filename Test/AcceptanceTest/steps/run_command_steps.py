__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from behave import *
from behave.api.async_step import async_run_until_complete
from discord import Reaction

from Utils.TestHelpers.TestIdGenerator import GLOBAL_ID_GENERATOR
from Utils.TestHelpers.embed_test_helper import parse_embed_from_table, create_error_embed, assert_same_embed_text
from Bot.DataClasses.ScrimChannel import ScrimChannel
from Utils.TestHelpers.ResponseLoggerContext import ResponseLoggerContext
from Utils.TestHelpers.id_parser import insert_ids
from Utils.TestHelpers.test_utils import create_mock_guild, create_mock_author, create_mock_channel,\
    create_async_mock_message


@given("channel registered for scrims")
@async_run_until_complete
async def step_impl(context):
    table = _create_call_ids(context)
    await call_command(';register', context, table)
    ResponseLoggerContext.get_oldest()


@given("a scrim on channel {channel_id}")
@async_run_until_complete
async def step_impl(context, channel_id):
    table = [["1", channel_id, "1"]]
    await call_command(';register', context, table)
    await call_command(';scrim dota', context, table)
    ResponseLoggerContext.get_oldest()
    context.latest_fetched = ResponseLoggerContext.get_oldest()


@given("a {game} scrim")
@async_run_until_complete
async def step_impl(context, game):
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
    if not alternative_text_channel:
        context.discord_ids["channel_id"] =\
            context.discord_ids.pop("channel_id", GLOBAL_ID_GENERATOR.generate_viable_id())
    else:
        context.discord_ids["text_2_id"] = \
            context.discord_ids.pop("text_2_id", GLOBAL_ID_GENERATOR.generate_viable_id())
    context.discord_ids["guild_id"] = context.discord_ids.pop("guild_id", GLOBAL_ID_GENERATOR.generate_viable_id())
    context.discord_ids["user_id"] = context.discord_ids.pop("user_id", GLOBAL_ID_GENERATOR.generate_viable_id())
    return [[context.discord_ids["user_id"],
             context.discord_ids["channel_id" if not alternative_text_channel else "text_2_id"],
             context.discord_ids["guild_id"]]]


async def call_command(command, context, table):
    for row in table:
        mock_guild = create_mock_guild(int(row[2]))
        mock_author = create_mock_author(int(row[0]), mock_guild)
        mock_channel = create_mock_channel(int(row[1]), mock_guild)
        mock_message = create_async_mock_message(mock_guild, mock_channel, mock_author, command)
        context.patcher.try_add_group(mock_channel)
        with context.patcher.patch_all():
            await context.client.on_message(mock_message)


@then("channel registered")
@async_run_until_complete
async def step_impl(context):
    channel = await ScrimChannel.convert(MagicMock(), int(context.discord_ids["channel_id"]))
    assert channel


@then("embed received with fields")
@async_run_until_complete
async def step_impl(context):
    embed = parse_embed_from_table(context)
    context.latest_fetched = ResponseLoggerContext.get_oldest()
    assert_same_embed_text(embed, context.latest_fetched.embeds[0])


@then("error and help received with message")
@async_run_until_complete
async def step_impl(context):
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


@when("{amount} user reacts with {reaction_string}")
@when("{amount} users react with {reaction_string}")
@async_run_until_complete
async def step_impl(context, amount, reaction_string):
    guild = create_mock_guild(1)
    user_increment = 1
    while f"user_{user_increment}_id" in context.discord_ids:
        user_increment += 1
    for _ in range(int(amount)):
        user = create_mock_author(GLOBAL_ID_GENERATOR.generate_viable_id(), guild)
        context.discord_ids[f"user_{user_increment}_id"] = user.id
        user_increment += 1
        reaction = Reaction(data={}, message=context.latest_fetched, emoji=reaction_string)
        context.client.dispatch("reaction_add", reaction, user)


@then("embed edited to have fields")
def step_impl(context):
    embed = parse_embed_from_table(context)
    assert_same_embed_text(embed, context.latest_fetched.embeds[0])
