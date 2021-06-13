__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import List, Dict

from Bot.DataClasses.Game import Game
from Bot.DataClasses.ScrimTeam import ScrimTeam
from Bot.Exceptions.BotBaseUserException import BotBaseUserException
from Bot.Exceptions.BotBaseInternalException import BotBaseInternalException


def _assert_valid_game(game):
    if game.team_count < 1:
        raise BotBaseInternalException("Tried to initialize a teams manager for a game with less than 1 teams.")
    if game.max_team_size and game.min_team_size > game.max_team_size:
        raise BotBaseInternalException("Tried to initialize a teams manager for a game with smaller team max size than"
                                       " team min size.")


class ScrimTeamsManager:
    """A class to be used inside a Scrim instance, meant for managing the separate teams in the scrim
    """
    PARTICIPANTS = "Participants"
    SPECTATORS = "Spectators"
    QUEUE = "Queue"

    def __init__(self, game: Game, team_channels: List[int] = None, lobby: int = None, *, teams: List[ScrimTeam] = None):
        _assert_valid_game(game)
        self._game = game
        self._build_standard_teams()
        self._build_teams(teams or [])
        self._captains = self._build_captains()
        self._team_channels = [lobby]
        self._team_channels = team_channels or []

    @classmethod
    def is_reserved_name(cls, team_name: str):
        return team_name in [cls.PARTICIPANTS, cls.SPECTATORS, cls.QUEUE]

    def get_standard_teams(self):
        return list(self._teams.values())[:3]

    def get_game_teams(self):
        if len(self._teams) > 3:
            return list(self._teams.values())[3:]
        return []

    def _build_standard_teams(self):
        self._teams: Dict[str, ScrimTeam] = {
            self.PARTICIPANTS: ScrimTeam(self.PARTICIPANTS, [], self._game.min_team_size * self._game.team_count,
                                         self._game.max_team_size * self._game.team_count),
            self.QUEUE: ScrimTeam(self.QUEUE),
            self.SPECTATORS: ScrimTeam(self.SPECTATORS)}

    def _build_teams(self, premade_teams):
        teams = []
        for i in range(self._game.team_count):
            if len(premade_teams) > i:
                self._add_premade_team(premade_teams[i])
            else:
                self._add_new_team(i+1)
        return teams

    def _add_new_team(self, team_number: int):
        team_name = f"Team {team_number}"
        self._teams[team_name] = ScrimTeam(team_name, [], self._game.min_team_size, self._game.max_team_size)

    def _add_premade_team(self, team: ScrimTeam):
        self._assert_valid_team(team)
        self._teams[team.name] = team

    def _assert_valid_team(self, team):
        self._assert_not_standard_team_name(team)
        self._assert_unique_team_name(team)
        self._assert_valid_team_size(team)
        self._assert_valid_team_players(team)

    def _assert_not_standard_team_name(self, team):
        if self.is_reserved_name(team.name):
            raise BotBaseUserException("Cannot create a scrim with a premade team name conflicting with a name "
                                       f"reserved for standard teams ({team.name})")

    def _assert_unique_team_name(self, team):
        if team.name in self._teams:
            raise BotBaseUserException(f"Cannot create a scrim with premade teams having identical names ({team.name})")

    def _assert_valid_team_size(self, team):
        if team.min_size != self._game.min_team_size or team.max_size != self._game.max_team_size:
            raise BotBaseUserException("Cannot create a scrim with a premade team with a size incompatible with the"
                                       f" chosen game ({team.name})")

    def _assert_valid_team_players(self, team):
        if len(team.players) > self._game.max_team_size:
            raise BotBaseUserException("Cannot create a scrim with a premade team with a size incompatible with the "
                                       f"chosen game ({team.name})")

    def _build_captains(self):
        captains = []
        for _ in range(self._game.team_count):
            captains.append(None)
        return captains
