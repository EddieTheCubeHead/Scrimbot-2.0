__version__ = "0.1"
__author__ = "Eetu Asikainen"

import asyncio
import io
from unittest.mock import patch

from behave import *
from behave.api.async_step import async_run_until_complete

from Bot.Core.ScrimBotLogger import ScrimBotLogger
from Utils.TestHelpers.DiscordPatcher import DiscordPatcher
from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.Core.ScrimBotClient import ScrimBotClient
from Configs.Config import Config
from Database.Core.MasterConnection import MasterConnection
from Utils.TestHelpers.ResponseMessageCatcher import ResponseMessageCatcher
from Utils.TestHelpers.test_utils import get_cogs_messages


@given("an uninitialized bot")
def step_impl(context):
    config = Config()
    logger = ScrimBotLogger(config)
    BotDependencyInjector.dependencies[MasterConnection] = MasterConnection(config, ":memory:")
    context.client = ScrimBotClient(config, logger, ResponseMessageCatcher())


@given("an initialized bot")
def step_impl(context):
    config = Config()
    logger = ScrimBotLogger(config)
    BotDependencyInjector.dependencies[MasterConnection] = MasterConnection(config, ":memory:")
    context.client = ScrimBotClient(config, logger, ResponseMessageCatcher())
    context.client.setup_cogs()
    context.patcher = DiscordPatcher()


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