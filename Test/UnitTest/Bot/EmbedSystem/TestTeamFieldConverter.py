__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

import discord

from Utils.UnittestBase import UnittestBase
from Utils.TestIdGenerator import TestIdGenerator
from Bot.EmbedSystem.TeamFieldConverter import TeamFieldConverter
from Bot.DataClasses.Team import Team


def _mock_player(name):
    player = MagicMock()
    player.display_name = name
    return player


def _bold(name):
    return f"**{discord.utils.escape_markdown(name)}**"


class TestTeamFieldConverter(UnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_mocker = TestIdGenerator()

    def test_convert_given_unlimited_sized_team_then_embed_correctly_formatted(self):
        team_players = self._mock_team_players(4)
        team_name = "Participants"
        mock_scrim_team = Team(team_name, team_players)
        result_field = TeamFieldConverter(mock_scrim_team).convert()
        team_players_string = "\n".join([player.display_name for player in team_players])
        self._assert_correct_field(result_field, _bold(team_name), team_players_string)

    def test_convert_given_empty_team_then_players_field_correctly_formatted(self):
        team_players = []
        team_name = "Participants"
        mock_scrim_team = Team(team_name, team_players)
        result_field = TeamFieldConverter(mock_scrim_team).convert()
        team_players_string = "__empty__"
        self._assert_correct_field(result_field, _bold(team_name), team_players_string)

    def test_convert_given_limited_sized_not_full_team_then_name_correctly_formatted(self):
        team_players = self._mock_team_players(4)
        team_name = "Team 1"
        mock_scrim_team = Team(team_name, team_players, 5)
        result_field = TeamFieldConverter(mock_scrim_team).convert()
        team_players_string = "\n".join([player.display_name for player in team_players])
        formatted_name = f"{_bold(team_name)} (1 needed)"
        self._assert_correct_field(result_field, formatted_name, team_players_string)

    def test_convert_given_min_size_reached_but_max_size_higher_then_name_correctly_formatted(self):
        team_players = self._mock_team_players(4)
        team_name = "Team 1"
        mock_scrim_team = Team(team_name, team_players, 3, 6)
        result_field = TeamFieldConverter(mock_scrim_team).convert()
        team_players_string = "\n".join([player.display_name for player in team_players])
        formatted_name = f"{_bold(team_name)} (fits 2 more)"
        self._assert_correct_field(result_field, formatted_name, team_players_string)

    def test_convert_given_min_size_is_max_size_and_max_size_reached_then_name_correctly_formatted(self):
        team_players = self._mock_team_players(7)
        team_name = "Team 1"
        mock_scrim_team = Team(team_name, team_players, 7)
        result_field = TeamFieldConverter(mock_scrim_team).convert()
        team_players_string = "\n".join([player.display_name for player in team_players])
        formatted_name = f"{_bold(team_name)} (full)"
        self._assert_correct_field(result_field, formatted_name, team_players_string)

    def test_convert_given_min_size_smaller_than_max_size_and_max_size_reached_then_name_correctly_formatted(self):
        team_players = self._mock_team_players(6)
        team_name = "Team 1"
        mock_scrim_team = Team(team_name, team_players, 2, 6)
        result_field = TeamFieldConverter(mock_scrim_team).convert()
        team_players_string = "\n".join([player.display_name for player in team_players])
        formatted_name = f"{_bold(team_name)} (full)"
        self._assert_correct_field(result_field, formatted_name, team_players_string)

    def test_convert_given_pickup_game_then_first_player_marked_captain(self):
        team_players = self._mock_team_players(6)
        team_name = "Team 1"
        mock_scrim_team = Team(team_name, team_players, 4, 8)
        mock_scrim_team.is_pickup = True
        result_field = TeamFieldConverter(mock_scrim_team).convert()
        escaped_player_names = [player.display_name for player in team_players]
        escaped_player_names[0] += TeamFieldConverter.CAPTAIN_MARK
        team_players_string = "\n".join(escaped_player_names)
        formatted_name = f"{_bold(team_name)} (fits 2 more)"
        self._assert_correct_field(result_field, formatted_name, team_players_string)

    def _mock_team_players(self, amount):
        players = []
        for _ in range(amount):
            players.append(_mock_player(str(self.id_mocker.generate_viable_id())))
        return players

    def _assert_correct_field(self, result_field, team_name, players_field):
        self.assertEqual(team_name, result_field.get_name())
        self.assertEqual(players_field, result_field.get_value())
        self.assertTrue(result_field.inline)
