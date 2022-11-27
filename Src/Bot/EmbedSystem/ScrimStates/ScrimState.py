__version__ = "0.1"
__author__ = "Eetu Asikainen"

import os
from abc import ABC, abstractmethod

from Bot.DataClasses.Scrim import Scrim
from Bot.DataClasses.Team import Team, QUEUE, SPECTATORS, PARTICIPANTS
from Bot.Logic.ScrimTeamsManager import ScrimTeamsManager


class ScrimState(ABC):

    _setup_team_names = (PARTICIPANTS, SPECTATORS, QUEUE)

    @staticmethod
    def build_team_participants(team: Team) -> str:
        if team.members:
            return os.linesep.join([f"<@!{member.user_id}>" for member in team.members])
        return "_empty_"

    def get_setup_teams(self, scrim: Scrim) -> list[Team]:
        setup_teams = []
        for team in scrim.teams:
            if team.name in self._setup_team_names:
                setup_teams.append(team)
        return setup_teams

    def get_game_teams(self, scrim: Scrim) -> list[Team]:
        game_teams = []
        for team in scrim.teams:
            if team.name not in self._setup_team_names:
                game_teams.append(team)
        return game_teams

    @property
    @abstractmethod
    def description(self) -> str:  # pragma: no cover
        pass

    @staticmethod
    @abstractmethod
    def build_description(teams_manager: ScrimTeamsManager) -> str:  # pragma: no cover
        pass

    @staticmethod
    @abstractmethod
    def build_fields(teams_manager: ScrimTeamsManager) -> list[(str, str, bool)]:  # pragma: no cover
        pass

    @staticmethod
    @abstractmethod
    def build_footer(teams_manager: ScrimTeamsManager) -> str:  # pragma: no cover
        pass
