__version__ = "0.1"
__author__ = "Eetu Asikainen"

from hintedi import HinteDI

from Src.Bot.DataClasses.Scrim import Scrim, ScrimState
from Src.Bot.EmbedSystem.ScrimStates.ScrimStateBase import ScrimStateBase


@HinteDI.singleton_implementation(base=ScrimStateBase, key=ScrimState.TERMINATED)
class TerminatedState(ScrimStateBase):

    @property
    def valid_transitions(self) -> list[ScrimState]:
        return []

    @property
    def description(self) -> str:
        return "terminated"

    def build_description(self, scrim: Scrim) -> str:
        if scrim.terminator_id:
            return f"Scrim terminated manually by <@{scrim.terminator_id}>"
        return "Scrim terminated automatically after inactivity"

    def build_fields(self, scrim: Scrim) -> list[(str, str, bool)]:
        return []

    def build_footer(self, scrim: Scrim) -> str:
        return "f"
