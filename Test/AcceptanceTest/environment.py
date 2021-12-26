__author__ = "Eetu Asikainen"

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.Core.Logging.BotClientLogger import BotClientLogger
from Bot.Core.ScrimBotClient import ScrimBotClient
from Configs.Config import Config
from Database.Core.MasterConnection import MasterConnection
from Utils.TestHelpers.DiscordPatcher import DiscordPatcher
from Utils.TestHelpers.ResponseLoggerContext import ResponseLoggerContext
from Utils.TestHelpers.ResponseMessageCatcher import ResponseMessageCatcher


def before_feature(context, feature):
    _setup_bot(context)
    if "no_init" not in feature.tags:
        context.client.setup_logging()
        context.client.load_games()
        context.client.setup_cogs()
        context.patcher = DiscordPatcher()


def _setup_bot(context):
    config = Config()
    logger = BotClientLogger(config)
    BotDependencyInjector.dependencies[MasterConnection] = MasterConnection(config, ":memory:")
    context.client = ScrimBotClient(config, logger, ResponseMessageCatcher())
    ResponseLoggerContext.reset()
