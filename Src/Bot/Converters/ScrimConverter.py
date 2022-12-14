__version__ = "0.1"
__author__ = "Eetu Asikainen"

from asyncio import Lock
from contextlib import asynccontextmanager

from discord import Message
from hintedi import HinteDI

from Bot.DataClasses.Game import Game
from Bot.DataClasses.ParticipantTeam import ParticipantTeam
from Bot.DataClasses.Scrim import Scrim, ScrimState
from Bot.DataClasses.ScrimChannel import ScrimChannel
from Bot.DataClasses.Team import PARTICIPANTS, SPECTATORS, QUEUE, Team
from Bot.DataClasses.User import User
from Bot.Exceptions.BotChannelHasScrimException import BotChannelHasScrimException
from Bot.Logic.ScrimManager import ScrimManager
from Database.DatabaseConnections.ScrimConnection import ScrimConnection


def _add_team_to_scrim(team_name: str, scrim: Scrim, min_size: int = 0, max_size: int = 0):
    team = Team(team_name)
    participant_team = ParticipantTeam(None, max_size, min_size)
    participant_team.team = team
    scrim.teams.append(participant_team)


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
                scrim = self._connection.get_active_scrim(channel_id)
                yield scrim
        finally:
            self._connection.edit_scrim(scrim)

    async def create_scrim(self, message: Message, game: Game) -> Scrim:
        scrim = Scrim(message, game)
        _add_team_to_scrim(PARTICIPANTS, scrim, scrim.game.min_team_size * scrim.game.team_count,
                           scrim.game.max_team_size * scrim.game.team_count)
        for team in (SPECTATORS, QUEUE):
            _add_team_to_scrim(team, scrim)
        for team_num in range(1, game.team_count + 1):
            _add_team_to_scrim(f"Team {team_num}", scrim, game.min_team_size, game.max_team_size)
        self._connection.add_scrim(scrim)
        return scrim

    def exists(self, channel_id: int) -> bool:
        return self._connection.exists(channel_id)
