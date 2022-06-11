from __future__ import annotations

__version__ = "0.1"
__author__ = "Eetu Asikainen"

import threading
from typing import Optional, TYPE_CHECKING

from discord import Message, Member

if TYPE_CHECKING:
    from Bot.Converters.ScrimResultConverter import ScrimResult
from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.DataClasses.Team import Team
from Bot.DataClasses.User import User
from Bot.EmbedSystem.ScrimStates.ScrimState import ScrimState
from Bot.EmbedSystem.ScrimStates.scrim_states import *
from Bot.Exceptions.BotInvalidStateChangeException import BotInvalidStateChangeException
from Bot.Exceptions.BuildException import BuildException
from Bot.Logic.ScrimTeamsManager import ScrimTeamsManager
from Bot.Exceptions.BotBaseRespondToContextException import BotBaseRespondToContextException
from Bot.Exceptions.BotLoggedContextException import BotLoggedContextException


class ScrimManager:

    def __init__(self, teams_manager: ScrimTeamsManager):
        self.teams_manager = teams_manager
        self.state: ScrimState = LFP
        self.message: Optional[Message] = None
        self.thread_lock = threading.Lock()

    def __hash__(self):
        if not self.message:
            raise BuildException("Tried to hash a scrim manager with no message")
        return self.message.id

    def build_description(self) -> str:
        return self.state.build_description(self.teams_manager)

    def build_fields(self) -> list[(str, str, bool)]:
        return self.state.build_fields(self.teams_manager)

    def build_footer(self) -> str:
        return self.state.build_footer(self.teams_manager)

    def add_participant(self, participant: User):
        self.teams_manager.add_player(ScrimTeamsManager.PARTICIPANTS, participant)

    def _secure_state_change(self, target_state: ScrimState, *valid_states: ScrimState):
        with self.thread_lock:
            if self.state not in valid_states:
                raise BotInvalidStateChangeException(self.state, target_state)
            self.state = target_state

    def lock(self):
        if not self.teams_manager.has_enough_participants:
            raise BotBaseRespondToContextException("Could not lock the scrim. Too few participants present.",
                                                   delete_after=60)
        self._secure_state_change(LOCKED, LFP)
        self.teams_manager.clear_queue()

    def start(self):
        self._assert_valid_starting_teams()
        self._secure_state_change(STARTED, LOCKED, CAPS)

    def _assert_valid_starting_teams(self):
        if not self.teams_manager.has_full_teams:
            raise BotBaseRespondToContextException("Could not start the scrim. Some teams lack the minimum number of "
                                                   "players required.", send_help=False)
        if self.teams_manager.has_participants:
            raise BotBaseRespondToContextException("Could not start the scrim. All participants are not in a team.",
                                                   send_help=False)

    async def start_with_voice(self) -> bool:
        self._assert_valid_starting_teams()
        self._secure_state_change(VOICE_WAIT, LOCKED, CAPS, VOICE_WAIT)
        if await self.teams_manager.try_move_to_voice():
            self._secure_state_change(STARTED, VOICE_WAIT)
            return True
        return False

    def cancel_voice_wait(self):
        self._secure_state_change(LOCKED, VOICE_WAIT)

    async def end(self, result: ScrimResult):
        self._secure_state_change(ENDED, STARTED)
        self.teams_manager.result = result
        await self.teams_manager.move_to_lobby()

    def terminate(self, author: Optional[Member]):
        self._secure_state_change(TERMINATED, LFP, LOCKED, CAPS_PREP, CAPS, VOICE_WAIT, STARTED)
        self.teams_manager.terminator = author.id
