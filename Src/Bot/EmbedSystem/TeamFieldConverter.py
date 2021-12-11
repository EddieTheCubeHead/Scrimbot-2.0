__version__ = "0.1"
__author__ = "Eetu Asikainen"

import discord

from Bot.EmbedSystem.EmbedField import EmbedField
from Bot.DataClasses.Team import Team


class TeamFieldConverter:

    CAPTAIN_MARK = " **(C)**"

    def __init__(self, team: Team):
        self.team = team

    def convert(self):
        formatted_players = self._format_player_list()
        formatted_name = self._format_name()
        return EmbedField(formatted_name, formatted_players, True)

    def _format_player_list(self):
        players_string = self._construct_players_string()
        return players_string or "__empty__"

    def _construct_players_string(self):
        cleaned_player_names = [discord.utils.escape_markdown(player.display_name) for player in self.team.members]
        if self.team.is_pickup:
            cleaned_player_names[0] += self.CAPTAIN_MARK
        players_string = "\n".join(cleaned_player_names)
        return players_string

    def _format_name(self):
        return f"**{discord.utils.escape_markdown(self.team.name)}**{self._get_name_qualifier()}"

    def _get_name_qualifier(self):
        if not self.team.max_size:
            return ""
        return self._construct_fullness_qualifier()

    def _construct_fullness_qualifier(self):
        if self.team.min_size > len(self.team.members):
            return f" ({self.team.min_size - len(self.team.members)} needed)"
        if self.team.max_size > len(self.team.members):
            return f" (fits {self.team.max_size - len(self.team.members)} more)"
        return " (full)"
