from Bot.EmbedSystem.ScrimStates.CaptainsPreparationState import CaptainsPreparationState
from Bot.EmbedSystem.ScrimStates.CaptainsState import CaptainsState
from Bot.EmbedSystem.ScrimStates.EndedState import EndedState
from Bot.EmbedSystem.ScrimStates.LockedState import LockedState
from Bot.EmbedSystem.ScrimStates.LookingForPlayersState import LookingForPlayersState
from Bot.EmbedSystem.ScrimStates.StartedState import StartedState
from Bot.EmbedSystem.ScrimStates.TerminatedState import TerminatedState
from Bot.EmbedSystem.ScrimStates.WaitingForVoiceState import WaitingForVoiceState

LFP = LookingForPlayersState()
LOCKED = LockedState()
STARTED = StartedState()
ENDED = EndedState()
CAPS = CaptainsState()
VOICE_WAIT = WaitingForVoiceState()
CAPS_PREP = CaptainsPreparationState()
TERMINATED = TerminatedState()
