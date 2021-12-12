__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from behave import *
from behave.api.async_step import async_run_until_complete

from Utils.TestHelpers.embed_test_helper import parse_embed_from_table, create_error_embed, assert_same_embed_text
from Bot.DataClasses.ScrimChannel import ScrimChannel
from Utils.TestHelpers.ResponseLoggerContext import ResponseLoggerContext
from Utils.TestHelpers.test_utils import create_mock_guild, create_mock_author, create_mock_channel,\
    create_async_mock_message


@step("channel '{channel}' registered for scrims in guild '{guild}'")
@async_run_until_complete
async def step_impl(context, channel, guild):
    context.table = [["1", channel, guild]]
    await call_command(';register', context)
    ResponseLoggerContext.get_oldest_embed()


@when("'{command}' is called with")
@async_run_until_complete
async def step_impl(context, command: str):
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
    assert_same_embed_text(embed, ResponseLoggerContext.get_oldest_embed())


@then("error received with message '{error_message}'")
@async_run_until_complete
async def step_impl(context, error_message):
    embed = create_error_embed(error_message)
    assert_same_embed_text(embed, ResponseLoggerContext.get_oldest_embed())


@then("error and help received with messages '{error_message}' and '{command}'")
@async_run_until_complete
async def step_impl(context, error_message, command):
    error_message = error_message.replace("\\", "")
    embed = create_error_embed(error_message, f"{command[0]}help {command[1:]}")
    assert_same_embed_text(embed, ResponseLoggerContext.get_oldest_embed())
