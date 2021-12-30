__version__ = "0.1"
__author__ = "Eetu Asikainen"

import os
from abc import ABC, abstractmethod

from Bot.DataClasses.Team import Team
from Bot.Logic.ScrimTeamsManager import ScrimTeamsManager


class ScrimState(ABC):

    @staticmethod
    def build_team_participants(team: Team):
        if team.members:
            return os.linesep.join([f"<@{member.user_id}>" for member in team.members])
        return "_empty_"

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
