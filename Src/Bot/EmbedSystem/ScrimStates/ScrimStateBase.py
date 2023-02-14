from __future__ import annotations

__version__ = "0.1"
__author__ = "Eetu Asikainen"

import os
from abc import ABC, abstractmethod

from hintedi import HinteDI

from Src.Bot.DataClasses.Scrim import Scrim, ScrimState
from Src.Bot.DataClasses.Team import Team, QUEUE, SPECTATORS, PARTICIPANTS
from Src.Bot.Exceptions.BotInvalidStateChangeException import BotInvalidStateChangeException


@HinteDI.abstract_base
class ScrimStateBase(ABC):

    _setup_teams = (PARTICIPANTS, SPECTATORS, QUEUE)

    @staticmethod
    def build_team_participants(team: Team) -> str:
        if team.members:
            return os.linesep.join([f"<@!{member.user_id}>" for member in team.members])
        return "_empty_"

    def get_setup_teams(self, scrim: Scrim) -> list[Team]:
        setup_teams = []
        for team in [participant_team.team for participant_team in scrim.teams]:
            if team.name in self._setup_teams:
                setup_teams.append(team)
        setup_teams.sort(key=lambda x: -1 if x.name not in self._setup_teams else self._setup_teams.index(x.name))
        return setup_teams

    def get_game_teams(self, scrim: Scrim) -> list[Team]:
        game_teams = []
        for team in [participant_team.team for participant_team in scrim.teams]:
            if team.name not in self._setup_teams:
                game_teams.append(team)
        return game_teams

    @property
    @abstractmethod
    def description(self) -> str:  # pragma: no cover
        pass

    @abstractmethod
    def build_description(self, scrim: Scrim) -> str:  # pragma: no cover
        pass

    @abstractmethod
    def build_fields(self, scrim: Scrim) -> list[(str, str, bool)]:  # pragma: no cover
        pass

    @abstractmethod
    def build_footer(self, scrim: Scrim) -> str:  # pragma: no cover
        pass

    @property
    @abstractmethod
    def valid_transitions(self) -> list[ScrimState]:
        pass

    @HinteDI.inject
    async def transition(self, scrim: Scrim, new_state: ScrimState, state_provider: ScrimStateBase) -> ScrimState:
        transitioned_state = state_provider.resolve_from_key(new_state)
        if new_state not in self.valid_transitions:
            raise BotInvalidStateChangeException(self, transitioned_state)
        self.validate_transition(scrim, new_state)
        await self.transition_hook(scrim, new_state)
        scrim.state = new_state
        return transitioned_state

    def validate_transition(self, scrim: Scrim, new_state: ScrimState):
        pass

    async def transition_hook(self, scrim: Scrim, new_state: ScrimState):
        pass

