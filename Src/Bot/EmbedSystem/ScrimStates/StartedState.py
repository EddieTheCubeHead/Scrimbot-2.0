__version__ = "0.1"
__author__ = "Eetu Asikainen"

from hintedi import HinteDI

from Bot.DataClasses.Scrim import Scrim, ScrimState
from Bot.EmbedSystem.ScrimStates.ScrimStateBase import ScrimStateBase


@HinteDI.singleton_implementation(base=ScrimStateBase, key=ScrimState.STARTED)
class StartedState(ScrimStateBase):

    @property
    def description(self) -> str:
        return "underway"

    @staticmethod
    def build_description(scrim: Scrim) -> str:
        description_string = f"{scrim.game.name} scrim underway. Declare the winner with the command 'winner ["
        if scrim.game.team_count > 1:
            description_string += "team]' "
            if scrim.game.team_count == 2:
                description_string += "or 'tie' "
        else:
            description_string += "user]' "
            if scrim.game.max_team_size == 2:
                description_string += "or 'tie' "
        description_string += "or end the scrim without declaring a winner with 'end'."
        return description_string

    def build_fields(self, scrim: Scrim) -> list[(str, str, bool)]:
        fields = []
        for team in self.get_game_teams(scrim):
            fields.append((team.name, self.build_team_participants(team), True))
        return fields

    @staticmethod
    def build_footer(scrim: Scrim) -> str:
        return "gl hf!"
