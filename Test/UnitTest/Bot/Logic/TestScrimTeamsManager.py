__version__ = "0.1"
__author__ = "Eetu Asikainen"

import unittest
from unittest.mock import MagicMock
from typing import Callable

from Bot.DataClasses.Game import Game
from Bot.DataClasses.ScrimTeam import ScrimTeam
from Bot.Logic.ScrimTeamsManager import ScrimTeamsManager
from Bot.Exceptions.BotBaseUserException import BotBaseUserException
from Bot.Exceptions.BotBaseInternalException import BotBaseInternalException


def _setup_manager(min_size, max_size, team_count):
    mock_game = _create_mock_game(min_size, max_size, team_count)
    return ScrimTeamsManager(mock_game)


def _create_mock_game(min_size, max_size, team_count):
    mock_game = Game("Test", "0xffffff", "icon", min_size, max_size, team_count)
    return mock_game


class TestScrimTeamsManager(unittest.TestCase):

    def test_init_given_team_count_zero_then_internal_error_raised(self):
        mock_game = _create_mock_game(5, 5, 0)
        expected_exception = BotBaseInternalException("Tried to initialize a teams manager for a game with less than 1 "
                                                      "teams.")
        self._assert_raises_correct_exception(expected_exception, ScrimTeamsManager, mock_game)

    def test_init_given_team_min_size_larger_than_max_size_when_max_size_not_zero_then_internal_error_raised(self):
        mock_game = _create_mock_game(5, 3, 1)
        expected_exception = BotBaseInternalException("Tried to initialize a teams manager for a game with smaller team"
                                                      " max size than team min size.")
        self._assert_raises_correct_exception(expected_exception, ScrimTeamsManager, mock_game)

    def test_init_given_team_min_size_larger_than_max_size_when_unlimited_max_size_then_init_successful(self):
        _setup_manager(5, 0, 1)

    def test_init_given_premade_team_when_team_name_conflicts_with_standard_teams_then_error_raised(self):
        mock_game = _create_mock_game(5, 5, 2)
        invalid_team = ScrimTeam(ScrimTeamsManager.PARTICIPANTS)
        expected_exception = BotBaseUserException("Cannot create a scrim with a premade team name conflicting with a "
                                                  "name reserved for standard teams"
                                                  f" ({ScrimTeamsManager.PARTICIPANTS})")
        self._assert_raises_correct_exception(expected_exception, ScrimTeamsManager, mock_game, teams=[invalid_team])

    def test_init_given_duplicate_premade_team_names_then_error_raised(self):
        mock_game = _create_mock_game(5, 5, 2)
        duplicate_name = "Duplicate team"
        team_1 = ScrimTeam(duplicate_name, [], 5, 5)
        team_2 = ScrimTeam(duplicate_name, [], 5, 5)
        expected_exception = BotBaseUserException("Cannot create a scrim with premade teams having identical names"
                                                  f" ({duplicate_name})")
        self._assert_raises_correct_exception(expected_exception, ScrimTeamsManager, mock_game, teams=[team_1, team_2])

    def test_init_given_duplicate_premade_team_names_when_name_conflicts_with_standard_teams_then_error_raised(self):
        mock_game = _create_mock_game(5, 5, 2)
        duplicate_name = ScrimTeamsManager.SPECTATORS
        team_1 = ScrimTeam(duplicate_name)
        team_2 = ScrimTeam(duplicate_name)
        expected_exception = BotBaseUserException("Cannot create a scrim with a premade team name conflicting with a "
                                                  "name reserved for standard teams"
                                                  f" ({duplicate_name})")
        self._assert_raises_correct_exception(expected_exception, ScrimTeamsManager, mock_game, teams=[team_1, team_2])

    def test_init_given_invalid_sized_premade_team_min_players_then_error_raised(self):
        mock_game = _create_mock_game(5, 5, 2)
        team_name = "Invalid team"
        invalid_team = ScrimTeam(team_name, [], 3, 5)
        expected_exception = BotBaseUserException("Cannot create a scrim with a premade team with a size incompatible"
                                                  f" with the chosen game ({team_name})")
        self._assert_raises_correct_exception(expected_exception, ScrimTeamsManager, mock_game, teams=[invalid_team])

    def test_init_given_invalid_sized_premade_team_max_players_then_error_raised(self):
        mock_game = _create_mock_game(5, 5, 2)
        team_name = "Invalid team"
        invalid_team = ScrimTeam(team_name, [], 5, 7)
        expected_exception = BotBaseUserException("Cannot create a scrim with a premade team with a size incompatible"
                                                  f" with the chosen game ({team_name})")
        self._assert_raises_correct_exception(expected_exception, ScrimTeamsManager, mock_game, teams=[invalid_team])

    def test_init_given_premade_team_with_too_many_players_then_error_raised(self):
        mock_game = _create_mock_game(5, 5, 2)
        team_name = "Invalid team"
        mock_players = [MagicMock() for _ in range(6)]
        invalid_team = ScrimTeam(team_name, mock_players, 5, 5)
        expected_exception = BotBaseUserException("Cannot create a scrim with a premade team with a size incompatible"
                                                  f" with the chosen game ({team_name})")
        self._assert_raises_correct_exception(expected_exception, ScrimTeamsManager, mock_game, teams=[invalid_team])

    def test_get_standard_teams_given_valid_setup_then_all_standard_teams_returned(self):
        min_size, max_size, team_count = 5, 5, 2
        manager = _setup_manager(min_size, max_size, team_count)
        standard_teams = manager.get_standard_teams()
        self._assert_valid_standard_teams(standard_teams, max_size, min_size, team_count)

    def test_get_game_teams_given_valid_setup_when_no_premade_teams_then_correct_teams_returned(self):
        min_size, max_size, team_count = 5, 6, 4
        manager = _setup_manager(min_size, max_size, team_count)
        game_teams = manager.get_game_teams()
        self._assert_valid_game_teams(game_teams, max_size, min_size, team_count)

    def test_get_game_teams_given_valid_setup_with_partly_premade_teams_then_correct_teams_returned(self):
        min_size, max_size, team_count = 5, 6, 4
        mock_game = _create_mock_game(min_size, max_size, team_count)
        mock_team = ScrimTeam("Premade team", [], min_size, max_size)
        manager = ScrimTeamsManager(mock_game, teams=[mock_team])
        game_teams = manager.get_game_teams()
        self.assertEqual(mock_team, game_teams[0])
        self._assert_valid_game_teams(game_teams, max_size, min_size, team_count)

    def test_get_game_teams_given_valid_setup_with_only_premade_teams_then_correct_teams_returned(self):
        min_size, max_size, team_count = 5, 6, 4
        mock_game = _create_mock_game(min_size, max_size, team_count)
        mock_teams = [ScrimTeam(f"Premade {i + 1}", [], min_size, max_size) for i in range(team_count)]
        manager = ScrimTeamsManager(mock_game, teams=mock_teams)
        game_teams = manager.get_game_teams()
        self.assertEqual(mock_teams, game_teams)
        self._assert_valid_game_teams(game_teams, max_size, min_size, team_count)

    def test_add_player_given_valid_team_name_and_not_full_team_then_insert_successful(self):
        pass

    def _assert_valid_standard_teams(self, standard_teams, max_size, min_size, team_count):
        for team_name in [ScrimTeamsManager.PARTICIPANTS, ScrimTeamsManager.SPECTATORS, ScrimTeamsManager.QUEUE]:
            self.assertIn(team_name, [team.name for team in standard_teams])
        self.assertEqual(min_size * team_count, standard_teams[0].min_size)
        self.assertEqual(max_size * team_count, standard_teams[0].min_size)
        self.assertEqual(0, standard_teams[1].min_size)
        self.assertEqual(0, standard_teams[1].max_size)
        self.assertEqual(0, standard_teams[2].min_size)
        self.assertEqual(0, standard_teams[2].max_size)

    def _assert_valid_game_teams(self, game_teams, max_size, min_size, team_count):
        self.assertEqual(team_count, len(game_teams))
        for team in game_teams:
            self.assertEqual(min_size, team.min_size)
            self.assertEqual(max_size, team.max_size)

    def _assert_raises_correct_exception(self, excepted_exception: Exception, call: Callable, *args, **kwargs):
        with self.assertRaises(type(excepted_exception)) as context:
            call(*args, **kwargs)

        self.assertEqual(str(excepted_exception), str(context.exception))
