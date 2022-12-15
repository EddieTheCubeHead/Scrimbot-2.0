from __future__ import annotations

__version__ = "0.1"
__author__ = "Eetu Asikainen"

import threading
from typing import Optional, TYPE_CHECKING

from discord import Message, Member
from hintedi import HinteDI

if TYPE_CHECKING:
    from Src.Bot.Converters.ScrimResultConverter import ScrimResult
    from Src.Bot.DataClasses.Scrim import ScrimState, Scrim
from Src.Bot.DataClasses.Team import Team
from Src.Bot.DataClasses.User import User
from Src.Bot.EmbedSystem.ScrimStates.ScrimStateBase import ScrimStateBase
from Src.Bot.Exceptions.BotInvalidStateChangeException import BotInvalidStateChangeException
from Src.Bot.Exceptions.BuildException import BuildException
from Src.Bot.Logic.ScrimTeamsManager import ScrimTeamsManager
from Src.Bot.Exceptions.BotBaseRespondToContextException import BotBaseRespondToContextException
from Src.Bot.Exceptions.BotLoggedContextException import BotLoggedContextException


class ScrimManager:

    @HinteDI.inject
    def __init__(self, scrim: Scrim, state: ScrimStateBase):
        self.scrim = scrim
        self.state: ScrimStateBase = state.resolve_from_key(scrim.state)
        self.message: Optional[Message] = None
        self.thread_lock = threading.Lock()

    def __hash__(self):
        if not self.message:
            raise BuildException("Tried to hash a scrim manager with no message")
        return self.message.id

    def build_description(self) -> str:
        return self.state.build_description(self.scrim)

    def build_fields(self) -> list[(str, str, bool)]:
        return self.state.build_fields(self.scrim)

    def build_footer(self) -> str:
        return self.state.build_footer(self.scrim)

    def _secure_state_change(self, target_state: ScrimStateBase, *valid_states: ScrimStateBase):
        with self.thread_lock:
            if self.state not in valid_states:
                raise BotInvalidStateChangeException(self.state, target_state)
            self.state = target_state
