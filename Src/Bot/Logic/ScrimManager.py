from __future__ import annotations

__version__ = "0.1"
__author__ = "Eetu Asikainen"

import threading
from typing import Optional

from discord import Message

from Bot.DataClasses.User import User
from Bot.EmbedSystem.ScrimStates.ScrimState import ScrimState
from Bot.EmbedSystem.ScrimStates.scrim_states import *
from Bot.Exceptions.BotInvalidStateChangeException import BotInvalidStateChangeException
from Bot.Logic.ScrimTeamsManager import ScrimTeamsManager
from Bot.Exceptions.BotBaseRespondToContextException import BotBaseRespondToContextException
from Bot.Exceptions.BotLoggedContextException import BotLoggedContextException


class ScrimManager:

    def __init__(self, teams_manager: ScrimTeamsManager):
        self.teams_manager = teams_manager
        self.state: ScrimState = LFP
        self.message: Optional[Message] = None
        self.thread_lock = threading.Lock()

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

    def start_with_voice(self):
        self._assert_valid_starting_teams()
        self._secure_state_change(VOICE_WAIT, LOCKED, CAPS)
        if self.teams_manager.try_move_to_voice():
            pass
