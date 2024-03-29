__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Bot.Converters.GameConverter import GameConverter
from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.Core.Logging.BotClientLogger import BotClientLogger
from Bot.Core.ScrimBotClient import ScrimBotClient
from Bot.Logic.DiscordVoiceChannelProvider import DiscordVoiceChannelProvider
from Bot.Logic.ScrimParticipantProvider import ScrimParticipantProvider
from Configs.Config import Config
from Database.Core.MasterConnection import MasterConnection
from Database.DatabaseConnections.GameConnection import GameConnection
from Test.Utils.TestHelpers.DiscordPatcher import DiscordPatcher
from Test.Utils.TestHelpers.ResponseLoggerContext import ResponseLoggerContext
from Test.Utils.TestHelpers.ResponseMessageCatcher import ResponseMessageCatcher
from Test.Utils.TestHelpers.UserFetchPatcher import UserFetchPatcher
from Test.Utils.TestHelpers.MockMemberConverter import MockMemberConverter
from Test.Utils.TestHelpers.TestIdGenerator import GLOBAL_ID_GENERATOR


def before_feature(context, feature):
    _setup_bot(context)
    if "no_init" not in feature.tags:
        context.client.setup_logging()
        context.client.load_games()
        context.client.setup_cogs()


def before_scenario(context, scenario):
    context.discord_ids = {"divider": "----------------------------------------------",
                           "user_id": GLOBAL_ID_GENERATOR.generate_viable_id()}
    context.command_messages = []
    context.mocked_users = {}
    context.patcher = DiscordPatcher()
    context.mock_context_provider.set_administrator_status("as_admin" in scenario.tags)
    context.patcher.add_patch("discord.ext.commands.converter.MemberConverter", MockMemberConverter())
    context.scrim_channel_registered = False
    _create_user_fetch_patcher(context)


def _setup_bot(context):
    config = Config()
    logger = BotClientLogger(config)
    BotDependencyInjector.dependencies[MasterConnection] = MasterConnection(config, ":memory:")
    BotDependencyInjector.dependencies[GameConnection] = GameConnection()
    BotDependencyInjector.dependencies[DiscordVoiceChannelProvider] = DiscordVoiceChannelProvider()
    BotDependencyInjector.dependencies[ScrimParticipantProvider] = ScrimParticipantProvider()
    BotDependencyInjector.dependencies[GameConverter] = GameConverter()
    context.mock_context_provider = ResponseMessageCatcher()
    context.client = ScrimBotClient(config, logger, context.mock_context_provider)
    ResponseLoggerContext.reset_position()


def _create_user_fetch_patcher(context):
    user_fetch_patcher = UserFetchPatcher(context)
    mock_guild = MagicMock()
    mock_guild.get_member = user_fetch_patcher
    mock_get = MagicMock()
    mock_get.return_value = mock_guild
    context.patcher.add_patch("discord.client.Client.get_guild", mock_get)
    return user_fetch_patcher
