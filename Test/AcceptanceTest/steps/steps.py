__version__ = "0.1"
__author__ = "Eetu Asikainen"

import asyncio
import io
from unittest.mock import patch, MagicMock

from discord.ext import commands
from behave import *
from behave.api.async_step import async_run_until_complete

from AcceptanceTest.steps.discord_mocker import *
from Bot.Core.BotDependencyConstructor import BotDependencyConstructor
from Bot.Core.ScrimClient import ScrimClient
from Bot.DataClasses.ScrimChannel import ScrimChannel
from Database.Core.MasterConnection import MasterConnection
from Utils.test_utils import get_cogs_messages


@given("a bot")
def step_impl(context):
    constructor = BotDependencyConstructor(MasterConnection(":memory:"))
    context.client = ScrimClient(constructor)


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
    for row in context.table[1:]:
        guild = create_mock_guild(row[2])
        user = create_mock_author(row[0], guild)
        channel = create_mock_channel(row[1], guild)
        message = create_mock_message(guild, channel, user, command)
        with patch("discord.ext.commands.Bot.get_context", create_mock_context(guild, user, message)):
            await context.client.on_message(command)


@then("channel '{channel_id}' registered")
@async_run_until_complete
async def step_impl(context, channel_id):
    channel = await ScrimChannel.convert(int(channel_id))
    assert channel
