from __future__ import annotations

__version__ = "0.1"
__author__ = "Eetu Asikainen"

from hintedi import HinteDI

from Src.Bot.DataClasses.Scrim import Scrim, ScrimState
from Src.Bot.DataClasses.Team import Team, QUEUE
from Src.Bot.EmbedSystem.ScrimStates.ScrimStateBase import ScrimStateBase
from Src.Bot.Exceptions.BotBaseRespondToContextException import BotBaseRespondToContextException


@HinteDI.singleton_implementation(base=ScrimStateBase, key=ScrimState.LFP)
class LookingForPlayersState(ScrimStateBase):

    @property
    def valid_transitions(self) -> list[ScrimState]:
        return [ScrimState.LOCKED]

    @property
    def description(self) -> str:
        return "looking for players"

    def build_description(self, scrim: Scrim) -> str:
        game = scrim.game
        min_players = game.team_count * game.min_team_size
        max_players = game.team_count * game.max_team_size
        current_players = len(self.get_setup_teams(scrim)[0].members)
        if current_players < min_players:
            return f"Looking for players, {min_players - current_players} more required."
        elif current_players <  max_players:
            return f"Enough players present. Room for {max_players - current_players} more. Send command 'lock' to " \
                   f"start team selection."
        return "All players present. Send command 'lock' to start team selection."

    def build_fields(self, scrim: Scrim) -> list[(str, str, bool)]:
        fields = []
        for team in self.get_setup_teams(scrim):
            if team.name == QUEUE and not team.members:
                continue
            fields.append((team.name, self.build_team_participants(team), True))
        return fields

    def build_footer(self, scrim: Scrim) -> str:
        game = scrim.game
        min_players = game.team_count * game.min_team_size
        current_players = len(self.get_setup_teams(scrim)[0].members)
        if current_players < min_players:
            return "To join players react 🎮 To join spectators react 👁"
        return "To join players react 🎮 To join spectators react 👁 To lock the teams send command 'lock'"

    def validate_transition(self, scrim: Scrim, new_state: ScrimState):
        participant_team: Team = self.get_setup_teams(scrim)[0]
        if len(participant_team.members) < scrim.game.team_count * scrim.game.min_team_size:
            raise BotBaseRespondToContextException("Could not lock the scrim. Too few participants present.",
                                                   delete_after=60)

    def transition_hook(self, scrim: Scrim, new_state: ScrimState):
        self.get_setup_teams(scrim)[2].members.clear()
