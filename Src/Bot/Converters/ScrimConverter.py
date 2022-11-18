__version__ = "0.1"
__author__ = "Eetu Asikainen"

from asyncio import Lock
from contextlib import asynccontextmanager

from hintedi import HinteDI

from Bot.DataClasses.Game import Game
from Bot.DataClasses.Scrim import Scrim
from Bot.DataClasses.ScrimChannel import ScrimChannel
from Bot.Exceptions.BotChannelHasScrimException import BotChannelHasScrimException
from Database.DatabaseConnections.ScrimConnection import ScrimConnection


@HinteDI.singleton
class ScrimConverter:

    @HinteDI.inject
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

    async def create_scrim(self, channel: ScrimChannel, game: Game) -> Scrim:
        await self._try_reserve_channel(channel.channel_id)
        scrim = Scrim(channel, game)
        self._connection.add_scrim(scrim)
        return scrim

    def exists(self, channel_id: int) -> bool:
        return self._connection.exists(channel_id)

    async def _try_reserve_channel(self, channel_id: int):
        if channel_id in self._scrims:
            raise BotChannelHasScrimException(channel_id)
        self._scrims[channel_id] = Lock()
        await self._scrims[channel_id].acquire()
