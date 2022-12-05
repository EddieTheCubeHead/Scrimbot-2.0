__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Bot.DataClasses.Scrim import Scrim
from Bot.EmbedSystem.ScrimStates.ScrimState import ScrimState


class TerminatedState(ScrimState):

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
