__version__ = "0.1"
__author__ = "Eetu Asikainen"

from hintedi import HinteDI

from Bot.DataClasses.Scrim import ScrimState, Scrim
from Bot.EmbedSystem.ScrimStates.ScrimStateBase import ScrimStateBase
from Bot.EmbedSystem.ScrimStates.StartedState import StartedState


@HinteDI.singleton_implementation(base=ScrimStateBase, key=ScrimState.VOICE_WAIT)
class WaitingForVoiceState(StartedState):

    @property
    def valid_transitions(self) -> list[ScrimState]:
        return []

    @property
    def description(self) -> str:
        return "waiting for players to join voice channel"

    def build_description(self, scrim: Scrim) -> str:
        return f"Starting {scrim.game.name} scrim. Waiting for all players to join voice chat..."

    def build_footer(self, scrim: Scrim) -> str:
        return "Scrim will start automatically when all players are in voice chat"
