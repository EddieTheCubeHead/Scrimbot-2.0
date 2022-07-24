__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Bot.DataClasses.Team import Team
from Bot.EmbedSystem.ScrimStates.StartedState import StartedState
from Bot.Logic.ScrimTeamsManager import ScrimTeamsManager


def _create_plural(teams: tuple[Team, ...]):
    return f"{', '.join([team.name for team in teams[:-1]])} and {teams[-1].name}"


class EndedState(StartedState):

    @staticmethod
    def build_description(teams_manager: ScrimTeamsManager) -> str:
        if len(teams_manager.result) < 1:
            return "Scrim has ended"
        elif len(teams_manager.result[0]) > 1:
            return f"Scrim has ended in a tie between {_create_plural(teams_manager.result[0])}"
        return f"Scrim has ended with {teams_manager.result[0][0].name} being victorious. Congratulations!"

    @staticmethod
    def build_footer(teams_manager: ScrimTeamsManager) -> str:
        return "gg wp!"
