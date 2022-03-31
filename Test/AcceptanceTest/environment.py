__author__ = "Eetu Asikainen"


from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.Core.Logging.BotClientLogger import BotClientLogger
from Bot.Core.ScrimBotClient import ScrimBotClient
from Bot.Logic.DiscordVoiceChannelProvider import DiscordVoiceChannelProvider
from Bot.Logic.ScrimParticipantProvider import ScrimParticipantProvider
from Configs.Config import Config
from Database.Core.MasterConnection import MasterConnection
from Test.Utils.TestHelpers.DiscordPatcher import DiscordPatcher
from Test.Utils.TestHelpers.ResponseLoggerContext import ResponseLoggerContext
from Test.Utils.TestHelpers.ResponseMessageCatcher import ResponseMessageCatcher
from Test.Utils.TestHelpers.UserFetchPatcher import UserFetchPatcher


def before_feature(context, feature):
    _setup_bot(context)
    if "no_init" not in feature.tags:
        context.client.setup_logging()
        context.client.load_games()
        context.client.setup_cogs()


def before_scenario(context, scenario):
    context.discord_ids = {"divider": "----------------------------------------------"}
    context.command_messages = []
    context.mocked_users = {}
    context.patcher = DiscordPatcher()
    _create_user_fetch_patcher(context)


def _setup_bot(context):
    config = Config()
    logger = BotClientLogger(config)
    BotDependencyInjector.dependencies[MasterConnection] = MasterConnection(config, ":memory:")
    BotDependencyInjector.dependencies[DiscordVoiceChannelProvider] = DiscordVoiceChannelProvider()
    BotDependencyInjector.dependencies[ScrimParticipantProvider] = ScrimParticipantProvider()
    context.client = ScrimBotClient(config, logger, ResponseMessageCatcher())
    ResponseLoggerContext.reset()


def _create_user_fetch_patcher(context):
    user_fetch_patcher = UserFetchPatcher(context)
    context.patcher.add_patch("discord.client.Client.get_user", user_fetch_patcher)
    return user_fetch_patcher
