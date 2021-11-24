__version__ = "0.1"
__author__ = "Eetu Asikainen"

import logging
from logging import Logger, DEBUG

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Configs.Config import Config


@BotDependencyInjector.singleton
class ScrimBotLogger(Logger):

    def __init__(self, config: Config):
        super().__init__("ScrimBotLogger")
        self.setLevel(DEBUG)
        handler = logging.FileHandler(filename=f'{config.file_folder}/scrim_bot.log', encoding='utf-8', mode='w')
        handler.setFormatter(logging.Formatter('%(asctime)s || %(levelname)s || %(message)s'))
        self.addHandler(handler)
