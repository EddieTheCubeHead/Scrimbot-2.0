__version__ = "0.1"
__author__ = "Eetu Asikainen"

from hintedi import HinteDI

from Src.Bot.DataClasses.Scrim import Scrim, ScrimState
from Src.Bot.DataClasses.Team import Team
from Src.Bot.EmbedSystem.ScrimStates.ScrimStateBase import ScrimStateBase
from Src.Bot.EmbedSystem.ScrimStates.StartedState import StartedState


def _create_plural(teams: list[Team]):
    return f"{', '.join([team.name for team in teams[:-1]])} and {teams[-1].name}"


def _get_winners(scrim: Scrim) -> list[Team]:
    winners = []
    for team in [participant_team.team for participant_team in scrim.teams]:
        if team.winner:
            winners.append(team)
    return winners


@HinteDI.singleton_implementation(base=ScrimStateBase, key=ScrimState.ENDED)
class EndedState(StartedState):

    @property
    def valid_transitions(self) -> list[ScrimState]:
        return []

    def build_description(self, scrim: Scrim) -> str:
        winners = _get_winners(scrim)
        if len(winners) < 1:
            return "Scrim has ended"
        elif len(winners) > 1:
            return f"Scrim has ended in a tie between {_create_plural(winners)}"
        return f"Scrim has ended with {winners[0].name} being victorious. Congratulations!"

    def build_footer(self, scrim: Scrim) -> str:
        return "gg wp!"
