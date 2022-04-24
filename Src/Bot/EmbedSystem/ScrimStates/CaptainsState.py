__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Bot.EmbedSystem.ScrimStates.ScrimState import ScrimState
from Bot.Logic.ScrimTeamsManager import ScrimTeamsManager


class CaptainsState(ScrimState):

    @property
    def description(self) -> str:
        return "letting captains pick players"

    @staticmethod
    def build_description(teams_manager: ScrimTeamsManager) -> str:
        pass

    @staticmethod
    def build_fields(teams_manager: ScrimTeamsManager) -> list[(str, str, bool)]:
        pass

    @staticmethod
    def build_footer(teams_manager: ScrimTeamsManager) -> str:
        pass
