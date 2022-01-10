__version__ = "0.1"
__author__ = "Eetu Asikainen"

import asyncio
import io
from unittest.mock import patch

from behave import *
from behave.api.async_step import async_run_until_complete

from Bot.Core.Logging.BotClientLogger import BotClientLogger
from Test.Utils.TestHelpers.DiscordPatcher import DiscordPatcher
from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.Core.ScrimBotClient import ScrimBotClient
from Configs.Config import Config
from Database.Core.MasterConnection import MasterConnection
from Test.Utils.TestHelpers.ResponseLoggerContext import ResponseLoggerContext
from Test.Utils.TestHelpers.ResponseMessageCatcher import ResponseMessageCatcher
from Test.Utils.TestHelpers.test_utils import get_cogs_messages


def _setup_bot(context):
    config = Config()
    logger = BotClientLogger(config)
    BotDependencyInjector.dependencies[MasterConnection] = MasterConnection(config, ":memory:")
    context.client = ScrimBotClient(config, logger, ResponseMessageCatcher())
    ResponseLoggerContext.reset()


@when("bot is started")
@async_run_until_complete
@patch('sys.stdout', new_callable=io.StringIO)
async def step_impl(context, print_capture):
    context.print_capture = print_capture
    context.client.load_games()
    context.client.setup_cogs()
    asyncio.create_task(context.client.start_bot())
    await context.client.connected.wait()
    await context.client.close()


@then("cogs are added")
def step_impl(context):
    for cog_message in get_cogs_messages():
        assert(cog_message in context.print_capture.getvalue().splitlines())


@then("connection to discord is established successfully")
def step_impl(context):
    assert("Attempting a connection to Discord..." in context.print_capture.getvalue().splitlines())
    assert(f"Successfully logged in as ScrimBot2.0, with version {__version__}"
           in context.print_capture.getvalue().splitlines())
