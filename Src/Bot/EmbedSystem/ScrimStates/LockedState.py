from Bot.DataClasses.Team import Team
from Bot.EmbedSystem.ScrimStates.ScrimState import ScrimState
from Bot.Logic.ScrimTeamsManager import ScrimTeamsManager

_divider = "----------------------------------------------"


def _get_fill_status(team: Team):
    if team.min_size > len(team.members):
        return f" _({team.min_size - len(team.members)} more needed)_"
    if team.max_size > len(team.members):
        return f" _(room for {team.max_size - len(team.members)} more)_"
    if team.max_size == len(team.members):
        return " _(full)_"


class LockedState(ScrimState):

    @property
    def description(self) -> str:
        return "waiting for team selection"

    @staticmethod
    def build_description(teams_manager: ScrimTeamsManager) -> str:
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
            name_text = team.name + _get_fill_status(team)
            fields.append((name_text, ScrimState.build_team_participants(team), True))

    @staticmethod
    def build_footer(teams_manager: ScrimTeamsManager) -> str:
        return "React 1️⃣ to join Team 1 or 2️⃣ to join Team 2"
