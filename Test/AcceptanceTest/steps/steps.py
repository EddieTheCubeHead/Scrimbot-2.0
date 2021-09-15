__version__ = "0.1"
__author__ = "Eetu Asikainen"

import asyncio
import io
from unittest.mock import patch, MagicMock

from behave import *
from behave.api.async_step import async_run_until_complete

from AcceptanceTest.steps.embed_test_helper import parse_embed_from_table, assert_same_embed_text
from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.Core.ScrimClient import ScrimClient
from Bot.DataClasses.ScrimChannel import ScrimChannel
from Configs.Config import Config
from Database.Core.MasterConnection import MasterConnection
from Utils.ResponseLoggerContext import ResponseLoggerContext
from Utils.ResponseMessageCatcher import ResponseMessageCatcher
from Utils.test_utils import get_cogs_messages, create_mock_guild, create_mock_author, create_mock_channel,\
    create_async_mock_message


@given("an uninitialized bot")
def step_impl(context):
    config = Config()
    BotDependencyInjector.dependencies[MasterConnection] = MasterConnection(config, ":memory:")
    context.client = ScrimClient(config, ResponseMessageCatcher())


@given("an initialized bot")
def step_impl(context):
    config = Config()
    BotDependencyInjector.dependencies[MasterConnection] = MasterConnection(config, ":memory:")
    context.client = ScrimClient(config, ResponseMessageCatcher())
    context.response_catcher = ResponseMessageCatcher()
    context.client.setup_cogs()


@when("bot is started")
@async_run_until_complete
@patch('sys.stdout', new_callable=io.StringIO)
async def step_impl(context, print_capture):
    context.print_capture = print_capture
    context.client.setup_cogs()
    asyncio.create_task(context.client.start_bot())
    await context.client.connected.wait()
    await context.client.close()


@then("cogs are added")
def step_impl(context):
    for cog_message in get_cogs_messages():
        assert(cog_message in context.print_capture.getvalue().splitlines())


@then("bot connects")
def step_impl(context):
    assert("Attempting a connection to Discord..." in context.print_capture.getvalue().splitlines())
    assert(f"Successfully logged in as ScrimBot2.0, with version {__version__}"
           in context.print_capture.getvalue().splitlines())


@when("'{command}' is called with")
@async_run_until_complete
async def step_impl(context, command: str):
    for row in context.table:
        mock_guild = create_mock_guild(row[2])
        mock_author = create_mock_author(row[0], mock_guild)
        mock_channel = create_mock_channel(row[1], mock_guild)
        mock_message = create_async_mock_message(mock_guild, mock_channel, mock_author, command)
        with patch("Bot.Core.ScrimClient.ScrimClient.user", MagicMock()):
            await context.client.on_message(mock_message)


@then("channel '{channel_id}' registered")
@async_run_until_complete
async def step_impl(context, channel_id):
    channel = await ScrimChannel.convert(int(channel_id))
    assert channel


@then("embed received with fields")
@async_run_until_complete
async def step_impl(context):
    embed = parse_embed_from_table(context.table)
    assert_same_embed_text(embed, ResponseLoggerContext.get_oldest_embed())
