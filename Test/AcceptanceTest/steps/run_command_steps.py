__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from behave import *
from behave.api.async_step import async_run_until_complete
from discord import Reaction, Emoji

from Utils.TestHelpers.embed_test_helper import parse_embed_from_table, create_error_embed, assert_same_embed_text
from Bot.DataClasses.ScrimChannel import ScrimChannel
from Utils.TestHelpers.ResponseLoggerContext import ResponseLoggerContext
from Utils.TestHelpers.test_utils import create_mock_guild, create_mock_author, create_mock_channel,\
    create_async_mock_message


@given("channel '{channel}' registered for scrims in guild '{guild}'")
@async_run_until_complete
async def step_impl(context, channel, guild):
    context.table = [["1", channel, guild]]
    await call_command(';register', context)
    ResponseLoggerContext.get_oldest()


@given("a scrim on channel {channel_id}")
@async_run_until_complete
async def step_impl(context, channel_id):
    context.table = [["1", channel_id, "1"]]
    await call_command(';register', context)
    await call_command(';scrim dota', context)
    ResponseLoggerContext.get_oldest()
    context.latest_fetched = ResponseLoggerContext.get_oldest()


@when("'{command}' is called with")
@async_run_until_complete
async def step_impl(context, command: str):
    context.latest_command = command.split(" ")[0][1:]
    context.latest_prefix = command[0]
    await call_command(command, context)


async def call_command(command, context):
    for row in context.table:
        mock_guild = create_mock_guild(int(row[2]))
        mock_author = create_mock_author(int(row[0]), mock_guild)
        mock_channel = create_mock_channel(int(row[1]), mock_guild)
        mock_message = create_async_mock_message(mock_guild, mock_channel, mock_author, command)
        context.patcher.try_add_group(mock_channel)
        with context.patcher.patch_all():
            await context.client.on_message(mock_message)


@then("channel '{channel_id}' registered")
@async_run_until_complete
async def step_impl(context, channel_id):
    channel = await ScrimChannel.convert(MagicMock(), int(channel_id))
    assert channel


@then("embed received with fields")
@async_run_until_complete
async def step_impl(context):
    embed = parse_embed_from_table(context.table)
    context.latest_fetched = ResponseLoggerContext.get_oldest()
    assert_same_embed_text(embed, context.latest_fetched.embeds[0])


@then("error received with message '{error_message}'")
@async_run_until_complete
async def step_impl(context, error_message):
    embed = create_error_embed(error_message, context.latest_command)
    context.latest_fetched = ResponseLoggerContext.get_oldest()
    assert_same_embed_text(embed, context.latest_fetched.embeds[0])


@then("error and help received with message '{error_message}'")
@async_run_until_complete
async def step_impl(context, error_message):
    error_message = error_message.replace("\\", "")
    embed = create_error_embed(error_message, context.latest_command,
                               f"{context.latest_prefix}help {context.latest_command}")
    context.latest_fetched = ResponseLoggerContext.get_oldest()
    assert_same_embed_text(embed, context.latest_fetched.embeds[0])


@then("team joining emojis reacted by bot")
def step_impl(context):
    message = context.latest_fetched
    assert "\U0001F3AE" in message.test_reactions
    assert "\U0001F441" in message.test_reactions


@when("user {user_id} reacts with {reaction_string}")
@async_run_until_complete
async def step_impl(context, user_id, reaction_string):
    guild = create_mock_guild(1)
    user = create_mock_author(user_id, guild)
    reaction = Reaction(data={}, message=context.latest_fetched, emoji=reaction_string)
    await context.client.dispatch("reaction_add", reaction, user)


@then("embed edited to have fields")
def step_impl(context):
    embed = parse_embed_from_table(context.table)
    assert_same_embed_text(embed, context.latest_fetched.embeds[0])
