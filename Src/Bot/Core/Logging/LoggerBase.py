__version__ = "0.1"
__author__ = "Eetu Asikainen"

import logging
from abc import ABC
from logging import Logger, DEBUG

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Configs.Config import Config


class LoggerBase(Logger, ABC):

    handler = None

    @BotDependencyInjector.inject
    def __init__(self, name: str, config: Config):
        super().__init__(name)
        self.setLevel(DEBUG)
        if self.handler is None:
            self.handler = logging.FileHandler(filename=f'{config.file_folder}/scrim_bot.log', encoding='utf-8',
                                               mode='w')
        handler = self.handler
        handler.setFormatter(logging.Formatter('%(name)-36s || %(asctime)s || %(levelname)-8s || %(message)s'))
        self.addHandler(handler)
