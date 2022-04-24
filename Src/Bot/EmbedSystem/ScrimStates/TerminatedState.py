__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Bot.EmbedSystem.ScrimStates.ScrimState import ScrimState
from Bot.Logic.ScrimTeamsManager import ScrimTeamsManager


class TerminatedState(ScrimState):

    @property
    def description(self) -> str:
        return "terminated"

    @staticmethod
    def build_description(teams_manager: ScrimTeamsManager) -> str:
        if teams_manager.terminator:
            return f"Scrim terminated manually by <@{teams_manager.terminator}>"
        return "Scrim terminated automatically after inactivity"

    @staticmethod
    def build_fields(teams_manager: ScrimTeamsManager) -> list[(str, str, bool)]:
        return []

    @staticmethod
    def build_footer(teams_manager: ScrimTeamsManager) -> str:
        return "f"
