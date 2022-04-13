__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Bot.EmbedSystem.ScrimStates.ScrimState import ScrimState
from Bot.Logic.ScrimTeamsManager import ScrimTeamsManager


class StartedState(ScrimState):

    @property
    def description(self) -> str:
        return "underway"

    @staticmethod
    def build_description(teams_manager: ScrimTeamsManager) -> str:
        description_string = f"{teams_manager.game.name} scrim underway. Declare the winner with the command 'winner ["
        if teams_manager.game.team_count > 1:
            description_string += "team]' "
            if teams_manager.game.team_count == 2:
                description_string += "or 'tie' "
        else:
            description_string += "user]' "
            if teams_manager.game.max_team_size == 2:
                description_string += "or 'tie' "
        description_string += "or end the scrim without declaring a winner with 'end'."
        return description_string

    @staticmethod
    def build_fields(teams_manager: ScrimTeamsManager) -> list[(str, str, bool)]:
        fields = []
        for team in teams_manager.get_game_teams():
            fields.append((team.name, ScrimState.build_team_participants(team), True))
        return fields

    @staticmethod
    def build_footer(teams_manager: ScrimTeamsManager) -> str:
        return "gl hf!"
