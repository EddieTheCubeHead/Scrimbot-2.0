__version__ = "0.1"
__author__ = "Eetu Asikainen"

from hintedi import HinteDI

from Bot.DataClasses.Scrim import Scrim, ScrimState
from Bot.EmbedSystem.ScrimStates.ScrimStateBase import ScrimStateBase


@HinteDI.singleton_implementation(base=ScrimStateBase, key=ScrimState.TERMINATED)
class TerminatedState(ScrimStateBase):

    @property
    def description(self) -> str:
        return "terminated"

    @staticmethod
    def build_description(scrim: Scrim) -> str:
        if scrim.terminator_id:
            return f"Scrim terminated manually by <@{scrim.terminator_id}>"
        return "Scrim terminated automatically after inactivity"

    @staticmethod
    def build_fields(scrim: Scrim) -> list[(str, str, bool)]:
        return []

    @staticmethod
    def build_footer(scrim: Scrim) -> str:
        return "f"
