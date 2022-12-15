__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Src.Bot.DataClasses.Scrim import Scrim, ScrimState
from Src.Bot.EmbedSystem.ScrimStates.ScrimStateBase import ScrimStateBase


class CaptainsPreparationState(ScrimStateBase):

    @property
    def valid_transitions(self) -> list[ScrimState]:
        return []

    @property
    def description(self) -> str:
        return "waiting to choose captains"

    def build_description(self, scrim: Scrim) -> str:
        pass

    def build_fields(self, scrim: Scrim) -> list[(str, str, bool)]:
        pass

    def build_footer(self, scrim: Scrim) -> str:
        pass
