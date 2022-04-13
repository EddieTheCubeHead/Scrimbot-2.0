from Bot.EmbedSystem.ScrimStates.StartedState import StartedState
from Bot.Logic.ScrimTeamsManager import ScrimTeamsManager


class EndedState(StartedState):

    @staticmethod
    def build_description(teams_manager: ScrimTeamsManager) -> str:
        if teams_manager.winner:
            return f"Scrim has ended with {teams_manager.winner} being victorious. Congratulations!"
        return "Scrim has ended"

    @staticmethod
    def build_footer(teams_manager: ScrimTeamsManager) -> str:
        return "gg wp!"
