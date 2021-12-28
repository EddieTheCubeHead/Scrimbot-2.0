from Bot.EmbedSystem.ScrimStates.ScrimState import ScrimState
from Bot.Logic.ScrimTeamsManager import ScrimTeamsManager


class CaptainsPreparationState(ScrimState):

    @property
    def description(self) -> str:
        return "waiting to choose captains"

    @staticmethod
    def build_description(teams_manager: ScrimTeamsManager) -> str:
        pass

    @staticmethod
    def build_fields(teams_manager: ScrimTeamsManager) -> list[(str, str, bool)]:
        pass

    @staticmethod
    def build_footer(teams_manager: ScrimTeamsManager) -> str:
        pass
