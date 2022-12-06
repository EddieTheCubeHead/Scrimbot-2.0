__version__ = "0.1"
__author__ = "Eetu Asikainen"

from hintedi import HinteDI

from Bot.DataClasses.Scrim import Scrim, ScrimState
from Bot.DataClasses.Team import Team, QUEUE, PARTICIPANTS
from Bot.EmbedSystem.ScrimStates.ScrimStateBase import ScrimStateBase

_divider = "----------------------------------------------"


def _get_team_fill_status(team: Team):
    if team.min_size > len(team.members):
        return f" _({team.min_size - len(team.members)} more needed)_"
    if team.max_size > len(team.members):
        return f" _(enough players: room for {team.max_size - len(team.members)} more)_"
    if team.max_size == len(team.members):
        return " _(full)_"


@HinteDI.singleton_implementation(base=ScrimStateBase, key=ScrimState.LOCKED)
class LockedState(ScrimStateBase):

    @property
    def valid_transitions(self) -> list[ScrimState]:
        return []

    @property
    def description(self) -> str:
        return "waiting for team selection"

    def build_description(self, scrim: Scrim) -> str:
        if scrim.has_full_teams and not scrim.has_participants:
            return "Teams full, use the command 'start' to start the scrim or 'teams clear' to clear teams"
        if not scrim.has_full_teams and not scrim.has_participants:
            return "No unassigned players left but all teams are not full! Please rebalance the teams with reactions " \
                   "or use the command 'teams _random/balanced/balancedrandom/pickup_'."
        return "Players locked. Use reactions for manual team selection or the command 'teams " \
               "_random/balanced/balancedrandom/pickup_' to define teams."

    def build_fields(self, scrim: Scrim) -> list[(str, str, bool)]:
        fields = self._build_standard_team_fields(scrim)
        fields.append((_divider, _divider, False))
        self._build_game_team_fields(fields, scrim)
        return fields

    def _build_standard_team_fields(self, scrim: Scrim):
        fields = []
        for team in self.get_setup_teams(scrim):
            if team.name == QUEUE:
                continue
            fields.append((team.name if team.name != PARTICIPANTS else "Unassigned",
                           self.build_team_participants(team), True))
        return fields

    def _build_game_team_fields(self, fields: list[(str, str)], scrim: Scrim):
        for team in self.get_game_teams(scrim):
            name_text = team.name + _get_team_fill_status(team)
            fields.append((name_text, ScrimStateBase.build_team_participants(team), True))

    def build_footer(self, scrim: Scrim) -> str:
        if self.has_full_teams(scrim) and not self.has_participants(scrim):
            return "Send command 'start' to start the scrim or send command 'teams clear' to clear teams"
        return "React 1️⃣ to join Team 1 or 2️⃣ to join Team 2"

    def has_full_teams(self, scrim: Scrim):
        for team in self.get_game_teams(scrim):
            if not len(team.members) >= team.min_size:
                return False
        return True

    def has_participants(self, scrim: Scrim):
        return len(self.get_setup_teams(scrim)[0].members) > 0
