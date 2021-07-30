from __future__ import annotations

__version__ = "0.1"
__author__ = "Eetu Asikainen"

import threading

import discord

from Bot.Logic.ScrimTeamsManager import ScrimTeamsManager
from Bot.DataClasses.ScrimState import ScrimState
from Bot.Exceptions.BotBaseUserException import BotBaseUserException
from Bot.Exceptions.BotBaseInternalException import BotBaseInternalException


class Scrim:

    def __init__(self, teams_manager: ScrimTeamsManager):
        self.teams_manager = teams_manager
        self.state = ScrimState.LFP
        self.thread_lock = threading.Lock()

    def add_participant(self, participant: discord.Member):
        self.teams_manager.add_player(ScrimTeamsManager.PARTICIPANTS, participant)

    def _secure_state_change(self, target_state: ScrimState, *valid_states: ScrimState):
        with self.thread_lock:
            if self.state not in valid_states:
                raise BotBaseInternalException("Tried to perform an invalid state change from state "
                                               f"{self.state.name} to {target_state.name}")
            self.state = target_state

    def lock(self):
        if not self.teams_manager.has_enough_participants:
            raise BotBaseUserException("Could not lock the scrim. Too few participants present.")
        self._secure_state_change(ScrimState.LOCKED, ScrimState.LFP)
        self.teams_manager.clear_queue()

    def start(self):
        self._assert_valid_starting_teams()
        self._secure_state_change(ScrimState.STARTED, ScrimState.LOCKED, ScrimState.CAPS)

    def _assert_valid_starting_teams(self):
        if not self.teams_manager.has_full_teams:
            raise BotBaseUserException("Could not start the scrim. Some teams lack the minimum number of players "
                                       "required.", send_help=False)
        if self.teams_manager.has_participants:
            raise BotBaseUserException("Could not start the scrim. All participants are not in a team.",
                                       send_help=False)

    def start_with_voice(self):
        self._assert_valid_starting_teams()
        self._secure_state_change(ScrimState.VOICE_WAIT, ScrimState.LOCKED, ScrimState.CAPS)
        if self.teams_manager.try_move_to_voice():
            pass
        pass
