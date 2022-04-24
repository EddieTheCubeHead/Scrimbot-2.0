__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Bot.DataClasses.Team import Team
from Bot.EmbedSystem.ScrimStates.ScrimState import ScrimState
from Bot.Logic.ScrimTeamsManager import ScrimTeamsManager

_divider = "----------------------------------------------"


def _get_team_fill_status(team: Team):
    if team.min_size > len(team.members):
        return f" _({team.min_size - len(team.members)} more needed)_"
    if team.max_size > len(team.members):
        return f" _(enough players: room for {team.max_size - len(team.members)} more)_"
    if team.max_size == len(team.members):
        return " _(full)_"


class LockedState(ScrimState):

    @property
    def description(self) -> str:
        return "waiting for team selection"

    @staticmethod
    def build_description(teams_manager: ScrimTeamsManager) -> str:
        if teams_manager.has_full_teams and not teams_manager.has_participants:
            return "Teams full, use the command 'start' to start the scrim or 'teams clear' to clear teams"
        if not teams_manager.has_full_teams and not teams_manager.has_participants:
            return "No unassigned players left but all teams are not full! Please rebalance the teams with reactions " \
                   "or use the command 'teams _random/balanced/balancedrandom/pickup_'."
        return "Players locked. Use reactions for manual team selection or the command 'teams " \
               "_random/balanced/balancedrandom/pickup_' to define teams."

    @staticmethod
    def build_fields(teams_manager: ScrimTeamsManager) -> list[(str, str, bool)]:
        fields = []
        LockedState._build_standard_team_fields(fields, teams_manager)
        fields.append((_divider, _divider, False))
        LockedState._build_game_team_fields(fields, teams_manager)
        return fields

    @staticmethod
    def _build_standard_team_fields(fields, teams_manager):
        for team in teams_manager.get_standard_teams():
            if team.name == ScrimTeamsManager.QUEUE:
                continue
            fields.append((team.name if team.name != ScrimTeamsManager.PARTICIPANTS else "Unassigned",
                           ScrimState.build_team_participants(team), True))

    @staticmethod
    def _build_game_team_fields(fields, teams_manager):
        for team in teams_manager.get_game_teams():
            name_text = team.name + _get_team_fill_status(team)
            fields.append((name_text, ScrimState.build_team_participants(team), True))

    @staticmethod
    def build_footer(teams_manager: ScrimTeamsManager) -> str:
        if teams_manager.has_full_teams and not teams_manager.has_participants:
            return "Send command 'start' to start the scrim or send command 'teams clear' to clear teams"
        return "React 1️⃣ to join Team 1 or 2️⃣ to join Team 2"
