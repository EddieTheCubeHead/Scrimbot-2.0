__version__ = "0.1"
__author__ = "Eetu Asikainen"

from asyncio import Lock
from contextlib import asynccontextmanager

from Bot.Converters.ScrimConverter import ScrimConverter
from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.DataClasses.Scrim import Scrim
from Bot.Logic.ScrimManager import ScrimManager


@BotDependencyInjector.singleton
class ScrimManagerConverter:

    @BotDependencyInjector.inject
    def __init__(self, scrim_converter: ScrimConverter):
        self._converter = scrim_converter

    def wrap_scrim(self, scrim: Scrim) -> ScrimManager:
        pass
