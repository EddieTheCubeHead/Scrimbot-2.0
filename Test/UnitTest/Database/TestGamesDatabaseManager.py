__version__ = "0.1"
__author__ = "Eetu Asikainen"

import unittest
import os
import shutil
import json
from typing import Dict, Union, Callable

import Test.test_utils as test_utils
from Database.GamesDatabaseManager import GamesDatabaseManager
from Database.DatabaseConnectionWrapper import DatabaseConnectionWrapper
from Database.Exceptions.DatabaseDuplicateUniqueRowException import DatabaseDuplicateUniqueRowException
from Database.Exceptions.DatabasePrimaryKeyViolatedException import DatabasePrimaryKeyViolatedException
from Database.Exceptions.DatabaseForeignKeyViolatedException import DatabaseForeignKeyViolatedException


def _setup_disposable_folder_manager(disposable_folder_name: str, disposable_file_name: str) -> \
        GamesDatabaseManager:
    disposable_folder_manager = GamesDatabaseManager(disposable_folder_name, disposable_file_name)
    if os.path.exists(disposable_folder_manager.db_folder_path):
        shutil.rmtree(disposable_folder_manager.db_folder_path)

    return disposable_folder_manager


class TestGamesDatabaseManager(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.manager: GamesDatabaseManager = GamesDatabaseManager.from_raw_file_path(":memory:")
        cls.manager.setup_manager()
        cls.id_mocker = test_utils.UniqueIdGenerator()

    def test_setup_given_uninitialized_folder_then_folder_created(self):
        disposable_folder = "DisposableGamesTest"
        disposable_manager = _setup_disposable_folder_manager(disposable_folder, "unused.db")
        disposable_manager.ensure_correct_folder_structure()
        self.assertIn(disposable_folder, os.listdir(disposable_manager.path))
        shutil.rmtree(disposable_manager.db_folder_path)

    def test_setup_given_normal_setup_then_all_tables_initialized(self):
        for table in ("Games", "Aliases", "Matches", "Participants", "UserElos"):
            self._assert_table_exists(table)

    def test_setup_given_normal_setup_then_all_games_initialized(self):
        with open(f"{self.manager.path}/games_init.json") as games_file:
            games: Dict[str, Dict[str, Union[str, int]]] = json.load(games_file)
            for game in games:
                self._assert_game_exists(game)

    def test_register_new_game_given_valid_game_with_no_aliases_then_operation_successful(self):
        mock_game = self._generate_mock_game()
        self.manager.register_new_game(mock_game)
        self._assert_game_exists(mock_game[0])

    def test_register_new_game_given_valid_game_with_aliases_then_operation_successful(self):
        mock_game = self._generate_mock_game()
        expected_aliases = ["test", "testing", "t"]
        self.manager.register_new_game(mock_game, expected_aliases)
        self._assert_game_exists(mock_game[0])
        actual_aliases = self._fetch_aliases(mock_game[0])
        expected_aliases.sort()
        actual_aliases.sort()
        self.assertListEqual(expected_aliases, actual_aliases)

    def test_register_new_game_given_game_exists_then_error_raised(self):
        mock_game = self._generate_mock_game()
        self._insert_game(mock_game)
        self._assert_raises_correct_exception(DatabaseDuplicateUniqueRowException("Games", "Name", mock_game[0]),
                                              self.manager.register_new_game, mock_game)

    def test_games_init_generator_given_database_exists_then_game_data_returned(self):
        games_data_generator = self.manager.games_init_generator()
        while True:
            try:
                game_data = next(games_data_generator)
                self._assert_tuple_is_valid_game_data(game_data)
            except StopIteration:
                break

    def test_insert_user_elo_given_valid_new_user_and_elo_then_elo_entry_created_correctly(self):
        valid_user_id = self.id_mocker.generate_viable_id()
        valid_elo_value = 1700
        self.manager.insert_player_elo(valid_user_id, "Dota 2", valid_elo_value)
        self._assert_elo_entry_equals(valid_user_id, "Dota 2", valid_elo_value)

    def test_insert_user_elo_given_duplicate_user_then_error_raised(self):
        user_id = self.id_mocker.generate_viable_id()
        elo_value = 1700
        self.manager.insert_player_elo(user_id, "Dota 2", elo_value)
        self._assert_raises_correct_exception(
            DatabasePrimaryKeyViolatedException("UserElos", ["Snowflake", "Game"], [str(user_id), "Dota 2"]),
            self.manager.insert_player_elo, user_id, "Dota 2", elo_value)

    def test_insert_user_elo_given_invalid_game_then_error_raised(self):
        user_id = self.id_mocker.generate_viable_id()
        self._assert_raises_correct_exception(DatabaseForeignKeyViolatedException("UserElos", "Game", "not valid",
                                                                                  "Games", "Name"),
                                              self.manager.insert_player_elo, user_id, "not valid", 1700)

    def test_add_match_given_valid_data_returns_new_match_id(self):
        valid_match_data = self._generate_mock_match("Dota 2", 2, 5)
        self._insert_player_elos(valid_match_data[0], valid_match_data[2])
        match_id = self.manager.add_match(*valid_match_data)
        self.assertEqual(int, type(match_id))
        self.assertTrue(match_id > 0)

    def _generate_mock_game(self):
        return str(self.id_mocker.generate_viable_id()), "color", "icon", 5, 5, 2

    def _generate_mock_match(self, game: str, team_count: int, team_amount: int, *, winner=1):
        players = []
        for team in range(team_count):
            for player in range(team_amount):
                players.append((self.id_mocker.generate_viable_id(), team + 1, 1700))

        return game, winner, players

    def _assert_table_exists(self, table: str):
        with DatabaseConnectionWrapper(self.manager.connection) as test_cursor:
            test_cursor.execute("SELECT Count(*) FROM sqlite_master WHERE type='table' AND name=?", (table,))
            self.assertEqual(test_cursor.fetchone()[0], 1, f"Expected to find table '{table}'")

    def _assert_game_exists(self, game_name: str):
        with DatabaseConnectionWrapper(self.manager.connection) as test_cursor:
            test_cursor.execute("SELECT Count(Name) FROM Games WHERE Name=?", (game_name,))

            self.assertEqual(1, test_cursor.fetchone()[0])

    def _insert_game(self, game_data):
        with DatabaseConnectionWrapper(self.manager.connection) as cursor:
            cursor.execute("INSERT INTO Games (Name, Colour, Icon, MinTeamSize, MaxTeamSize, TeamCount)"
                           "VALUES (?, ?, ?, ?, ?, ?)", game_data)

    def _fetch_aliases(self, game_name):
        with DatabaseConnectionWrapper(self.manager.connection) as cursor:
            cursor.execute("SELECT Alias FROM Aliases WHERE GameName=?", (game_name,))
            return [row[0] for row in cursor.fetchall()]

    def _assert_tuple_is_valid_game_data(self, game_data):
        # Ignore the aliases field as it is not a primitive type
        result_message = test_utils.assert_tuple_with_correct_types(game_data[:6], str, str, str, int, int, int)
        self.assertIsNone(result_message, result_message)

    def _assert_elo_entry_equals(self, player_id: int, game: str, expected_elo: int):
        with DatabaseConnectionWrapper(self.manager.connection) as cursor:
            cursor.execute("SELECT Elo FROM UserElos WHERE Snowflake=? AND Game=?", (player_id, game))
            self.assertEqual(expected_elo, cursor.fetchone()[0])

    def _assert_raises_correct_exception(self, excepted_exception: Exception, call: Callable, *args, **kwargs):
        with self.assertRaises(type(excepted_exception)) as context:
            call(*args, **kwargs)

        self.assertEqual(str(excepted_exception), str(context.exception))

    def _insert_player_elos(self, game, players):
        for player in players:
            self._insert_player_elo(game, player)

    def _insert_player_elo(self, game, player):
        with DatabaseConnectionWrapper(self.manager.connection) as cursor:
            cursor.execute("INSERT INTO UserElos(Game, Snowflake, Elo) VALUES (?, ?, ?)", (game, player[0], player[2]))


if __name__ == '__main__':
    unittest.main()
