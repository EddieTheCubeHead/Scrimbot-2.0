__version__ = "0.1"
__author__ = "Eetu Asikainen"

from asyncio import Lock
from contextlib import asynccontextmanager

from Bot.Converters.ScrimConverter import ScrimConverter
from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.Logic.ScrimManager import ScrimManager


@BotDependencyInjector.singleton
class ScrimManagerConverter:

    @BotDependencyInjector.inject
    def __init__(self, scrim_converter: ScrimConverter):
        self._converter = scrim_converter

    @asynccontextmanager
    async def wrap_scrim(self, channel_id: int) -> ScrimManager:
        async with self._converter.fetch_scrim(channel_id) as scrim:
            try:
                yield scrim
            finally:
                pass
