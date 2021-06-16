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


def _setup_manager(min_size = 5, max_size = 5, team_count = 2):
    mock_game = _create_mock_game(min_size, max_size, team_count)
    return ScrimTeamsManager(mock_game)


def _create_mock_game(min_size, max_size, team_count):
    mock_game = Game("Test", "0xffffff", "icon", min_size, max_size, team_count)
    return mock_game


def _fill_teams(manager, max_size, team_count):
    for team_index in range(team_count):
        for player_num in range(max_size):
            manager.add_player(team_index, MagicMock())


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

    def test_add_player_given_participants_not_full_when_player_added_to_participants_then_insert_successful(self):
        tester_name = "Tester"
        manager = _setup_manager()
        mock_player = MagicMock()
        mock_player.display_name = tester_name
        manager.add_player(manager.PARTICIPANTS, mock_player)
        updated_participants = manager.get_standard_teams()[0]
        self.assertIn(mock_player, updated_participants.players)

    def test_add_player_given_participants_full_when_player_added_to_participants_then_inserted_to_queue(self):
        min_size, max_size, team_count = 3, 3, 2
        tester_name = "Tester"
        manager = _setup_manager(min_size, max_size, team_count)
        for i in range(max_size * team_count):
            manager.add_player(manager.PARTICIPANTS, MagicMock())
        mock_player = MagicMock()
        mock_player.display_name = tester_name
        manager.add_player(manager.PARTICIPANTS, mock_player)
        updated_queue = manager.get_standard_teams()[2]
        self.assertIn(mock_player, updated_queue.players)

    def test_add_player_when_added_to_spectators_then_insert_successful(self):
        tester_name = "Tester"
        manager = _setup_manager()
        mock_player = MagicMock()
        mock_player.display_name = tester_name
        manager.add_player(manager.SPECTATORS, mock_player)
        updated_participants = manager.get_standard_teams()[1]
        self.assertIn(mock_player, updated_participants.players)

    def test_add_player_given_team_not_full_when_added_to_game_teams_with_team_name_then_insert_successful(self):
        min_size, max_size, team_count = 6, 6, 5
        tester_name = "Tester"
        manager = _setup_manager(min_size, max_size, team_count)
        mock_player = MagicMock()
        mock_player.display_name = tester_name
        for team in range(team_count):
            with self.subTest(f"Team {team + 1}"):
                manager.add_player(f"Team {team + 1}", mock_player)
                updated_participants = manager.get_game_teams()[team]
                self.assertIn(mock_player, updated_participants.players)

    def test_add_player_given_team_not_full_when_added_to_game_teams_with_team_number_then_insert_successful(self):
        min_size, max_size, team_count = 1, 3, 4
        tester_name = "Tester"
        manager = _setup_manager(min_size, max_size, team_count)
        mock_player = MagicMock()
        mock_player.display_name = tester_name
        for team in range(team_count):
            with self.subTest(f"Team {team + 1}"):
                manager.add_player(team, mock_player)
                updated_participants = manager.get_game_teams()[team]
                self.assertIn(mock_player, updated_participants.players)

    def test_add_player_given_team_full_when_added_to_game_team_then_error_raised(self):
        min_size, max_size, team_count = 1, 5, 4
        manager = _setup_manager(min_size, max_size, team_count)
        _fill_teams(manager, max_size, team_count)
        tester_name = "Tester"
        mock_player = MagicMock()
        mock_player.display_name = tester_name
        for team in range(team_count):
            with self.subTest(f"Team {team + 1}"):
                expected_exception = BotBaseInternalException(f"Tried adding a player into a "
                                                              f"full team (Team {team + 1})")
                self._assert_raises_correct_exception(expected_exception, manager.add_player, team, mock_player)

    def test_has_enough_participants_given_no_participants_then_false_returned(self):
        manager = _setup_manager()
        self.assertFalse(manager.has_enough_participants)

    def test_has_enough_participants_given_participants_under_min_team_size_times_team_count_then_false_returned(self):
        min_size, max_size, team_count = 2, 2, 8
        manager = _setup_manager(min_size, max_size, team_count)
        for _ in range(min_size*team_count - 1):
            manager.add_player(manager.PARTICIPANTS, MagicMock())
        self.assertFalse(manager.has_enough_participants)

    def test_has_enough_participants_given_participants_at_min_team_size_times_team_count_then_true_returned(self):
        min_size, max_size, team_count = 4, 8, 2
        manager = _setup_manager(min_size, max_size, team_count)
        for _ in range(min_size * team_count):
            manager.add_player(manager.PARTICIPANTS, MagicMock())
        self.assertTrue(manager.has_enough_participants)

    def test_has_enough_participants_given_participants_at_max_team_size_times_team_count_then_true_returned(self):
        min_size, max_size, team_count = 5, 9, 5
        manager = _setup_manager(min_size, max_size, team_count)
        for _ in range(max_size * team_count):
            manager.add_player(manager.PARTICIPANTS, MagicMock())
        self.assertTrue(manager.has_enough_participants)

    def test_remove_player_given_valid_standard_team_when_called_with_player_in_team_then_player_removed(self):
        manager = _setup_manager()
        mock_player = MagicMock()
        for index, team in enumerate([manager.PARTICIPANTS, manager.SPECTATORS, manager.QUEUE]):
            with self.subTest(team):
                manager.add_player(team, mock_player)
                manager.remove_player(team, mock_player)
                standard_teams = manager.get_standard_teams()
                self.assertNotIn(mock_player, standard_teams[index].players)

    def test_remove_player_given_valid_game_team_when_called_with_player_in_team_then_player_removed(self):
        min_size, max_size, team_count = 3, 5, 6
        manager = _setup_manager(min_size, max_size, team_count)
        mock_player = MagicMock()
        for team in range(team_count):
            with self.subTest(f"Team {team + 1}"):
                manager.add_player(team, mock_player)
                manager.remove_player(team, mock_player)
                game_teams = manager.get_game_teams()
                self.assertNotIn(mock_player, game_teams[team].players)

    def test_remove_player_given_valid_team_when_called_with_player_not_in_team_then_error_raised(self):
        manager = _setup_manager()
        player_name = "Invalid player"
        mock_player = MagicMock()
        mock_player.display_name = player_name
        expected_exception = BotBaseInternalException(f"Tried removing user '{player_name}' from team 'Team 1' "
                                                      f"even though they are not a member of the team.")
        self._assert_raises_correct_exception(expected_exception, manager.remove_player, 0, mock_player)

    def test_remove_player_given_queue_has_players_when_removed_from_participants_then_filled_from_queue(self):
        min_size, max_size, team_count = 3, 5, 6
        manager = _setup_manager(min_size, max_size, team_count)
        mock_player = MagicMock()
        for _ in range(max_size*team_count - 1):
            manager.add_player(manager.PARTICIPANTS, MagicMock())
        manager.add_player(manager.PARTICIPANTS, mock_player)
        manager.add_player(manager.QUEUE, MagicMock())
        manager.remove_player(manager.PARTICIPANTS, mock_player)
        standard_teams = manager.get_standard_teams()
        self.assertEqual(max_size*team_count, len(standard_teams[0].players))
        self.assertEqual(0, len(standard_teams[2].players))

    def test_set_team_given_valid_move_then_player_removed_from_original_team_and_added_to_new_team(self):
        manager = _setup_manager()
        mock_player = MagicMock()
        manager.add_player(manager.PARTICIPANTS, mock_player)
        manager.set_team(manager.SPECTATORS, mock_player)
        standard_teams = manager.get_standard_teams()
        self.assertEqual(0, len(standard_teams[0].players))
        self.assertEqual(1, len(standard_teams[1].players))

    def test_set_team_given_valid_move_when_moved_from_full_participants_and_queue_has_people_then_filled(self):
        min_size, max_size, team_count = 3, 5, 6
        manager = _setup_manager(min_size, max_size, team_count)
        mock_player = MagicMock()
        for _ in range(max_size * team_count - 1):
            manager.add_player(manager.PARTICIPANTS, MagicMock())
        manager.add_player(manager.PARTICIPANTS, mock_player)
        manager.add_player(manager.QUEUE, MagicMock())
        manager.set_team(manager.SPECTATORS, mock_player)
        standard_teams = manager.get_standard_teams()
        self.assertEqual(max_size * team_count, len(standard_teams[0].players))
        self.assertEqual(0, len(standard_teams[2].players))

    def test_set_team_given_player_not_in_any_team_then_error_raised(self):
        manager = _setup_manager()
        player_name = "Invalid player"
        mock_player = MagicMock()
        mock_player.display_name = player_name
        expected_exception = BotBaseInternalException(f"Tried setting team for user '{player_name}' who is not part "
                                                      f"of the scrim.")
        self._assert_raises_correct_exception(expected_exception, manager.set_team, manager.SPECTATORS, mock_player)
        standard_teams = manager.get_standard_teams()
        self.assertEqual(0, len(standard_teams[0].players))

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
