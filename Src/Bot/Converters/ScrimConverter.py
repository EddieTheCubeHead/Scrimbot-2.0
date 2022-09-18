__version__ = "0.1"
__author__ = "Eetu Asikainen"

from asyncio import Lock
from contextlib import asynccontextmanager

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.DataClasses.Scrim import Scrim
from Database.DatabaseConnections.ScrimConnection import ScrimConnection


@BotDependencyInjector.singleton
class ScrimConverter:

    @BotDependencyInjector.inject
    def __init__(self, connection: ScrimConnection):
        self._connection = connection
        self._scrims: dict[int: Lock] = {}

    @asynccontextmanager
    async def fetch_scrim(self, channel_id: int) -> Scrim:
        if channel_id not in self._scrims:
            self._scrims[channel_id] = Lock()
        try:
            async with self._scrims[channel_id]:
                yield self._connection.get_active_scrim(channel_id)
        finally:
            pass

    def exists(self, channel_id: int) -> bool:
        return self._connection.exists(channel_id)
