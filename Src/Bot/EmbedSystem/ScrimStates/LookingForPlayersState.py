from __future__ import annotations

__version__ = "0.1"
__author__ = "Eetu Asikainen"

import os

from Bot.DataClasses.Team import Team
from Bot.EmbedSystem.ScrimStates.ScrimState import ScrimState
from Bot.Logic.ScrimTeamsManager import ScrimTeamsManager


class LookingForPlayersState(ScrimState):

    @property
    def description(self) -> str:
        return "looking for players"

    @staticmethod
    def build_description(teams_manager: ScrimTeamsManager) -> str:
        game = teams_manager.game
        min_players = game.team_count * game.min_team_size
        max_players = game.team_count * game.max_team_size
        current_players = len(teams_manager.get_standard_teams()[0].members)
        if current_players < min_players:
            return f"Looking for players, {min_players - current_players} more required."
        elif current_players <  max_players:
            return f"Enough players present. Room for {max_players - current_players} more. Send command 'lock' to " \
                   f"start team selection."
        return "All players present. Send command 'lock' to start team selection."

    @staticmethod
    def build_fields(teams_manager: ScrimTeamsManager) -> list[(str, str, bool)]:
        fields = []
        for team in teams_manager.get_standard_teams():
            if team.name == ScrimTeamsManager.QUEUE and not team.members:
                continue
            fields.append((team.name, ScrimState.build_team_participants(team), True))
        return fields

    @staticmethod
    def build_footer(teams_manager: ScrimTeamsManager) -> str:
        game = teams_manager.game
        min_players = game.team_count * game.min_team_size
        current_players = len(teams_manager.get_standard_teams()[0].members)
        if current_players < min_players:
            return "To join players react 🎮 To join spectators react 👁"
        return "To join players react 🎮 To join spectators react 👁 To lock the teams send command 'lock'"
