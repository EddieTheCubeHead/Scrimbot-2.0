__version__ = "0.1"
__author__ = "Eetu Asikainen"

import unittest
import os
import shutil
import json
from typing import Dict, Union

import Test.test_utils as test_utils
from Utils.UnittestBase import UnittestBase
from Utils.TestIdGenerator import TestIdGenerator
from Database.GamesDatabaseManager import GamesDatabaseManager
from Database.DatabaseConnectionWrapper import DatabaseConnectionWrapper
from Bot.Exceptions.BotBaseInternalException import BotBaseInternalException
from Database.Exceptions.DatabaseMissingRowException import DatabaseMissingRowException
from Database.Exceptions.DatabaseDuplicateUniqueRowException import DatabaseDuplicateUniqueRowException
from Database.Exceptions.DatabasePrimaryKeyViolatedException import DatabasePrimaryKeyViolatedException
from Database.Exceptions.DatabaseForeignKeyViolatedException import DatabaseForeignKeyViolatedException


def _setup_disposable_folder_manager(disposable_folder_name: str, disposable_file_name: str) -> \
        GamesDatabaseManager:
    disposable_folder_manager = GamesDatabaseManager(disposable_folder_name, disposable_file_name)
    if os.path.exists(disposable_folder_manager.db_folder_path):
        shutil.rmtree(disposable_folder_manager.db_folder_path)

    return disposable_folder_manager


class TestGamesDatabaseManager(UnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.manager: GamesDatabaseManager = GamesDatabaseManager.from_raw_file_path(":memory:")
        cls.manager.setup_manager()
        cls.id_mocker = TestIdGenerator()

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
        with open(f"{self.manager.path}/../Configs/games_init.json") as games_file:
            games: Dict[str, Dict[str, Union[str, int]]] = json.load(games_file)
            for game in games:
                self._assert_game_exists(game)

    def test_setup_given_manager_used_before_setup_then_error_raised(self):
        new_manager = GamesDatabaseManager("Foo", "Bar")
        expected_error_message = f"Tried to use database in {new_manager.db_file_path} " \
                                 f"before the connection was set up."
        with self.assertRaises(BotBaseInternalException) as context:
            new_manager.insert_user_elo(self.id_mocker.generate_viable_id(), "Dota 2")
        self.assertEqual(expected_error_message, context.exception.get_message())

    def test_register_new_game_given_valid_game_with_no_aliases_then_operation_successful(self):
        mock_game = self._generate_mock_game()
        self.manager.register_new_game(mock_game)
        self._assert_game_exists(mock_game[0])

    def test_register_new_game_given_valid_game_with_aliases_then_operation_successful(self):
        mock_game = self._generate_mock_game()
        expected_aliases = ["test_alias", "testing_alias", "t_alias"]
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

    def test_register_new_game_given_duplicate_alias_then_error_raised(self):
        alias = "TestAlias"
        game_1 = self._generate_mock_game()
        game_2 = self._generate_mock_game()
        self._insert_game(game_1)
        self._insert_aliases(game_1[0], [alias])
        expected_exception = DatabaseDuplicateUniqueRowException("Aliases", "Alias", alias)
        self._assert_raises_correct_exception(expected_exception, self.manager.register_new_game, game_2, [alias])

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
        self.manager.insert_user_elo(valid_user_id, "Dota 2", valid_elo_value)
        self._assert_elo_entry_equals(valid_user_id, "Dota 2", valid_elo_value)

    def test_insert_user_elo_given_duplicate_user_then_error_raised(self):
        user_id = self.id_mocker.generate_viable_id()
        elo_value = 1700
        self.manager.insert_user_elo(user_id, "Dota 2", elo_value)
        self._assert_raises_correct_exception(
            DatabasePrimaryKeyViolatedException("UserElos", ["Snowflake", "Game"], [str(user_id), "Dota 2"]),
            self.manager.insert_user_elo, user_id, "Dota 2", elo_value)

    def test_insert_user_elo_given_no_elo_value_then_default_value_used(self):
        user_id = self.id_mocker.generate_viable_id()
        default_elo = 1700
        self.manager.insert_user_elo(user_id, "Dota 2")
        self._assert_elo_entry_equals(user_id, "Dota 2", default_elo)

    def test_insert_user_elo_given_elo_under_zero_then_error_raised(self):
        user_id = self.id_mocker.generate_viable_id()
        invalid_elo = -1
        self.assertRaises(BotBaseInternalException, self.manager.insert_user_elo, user_id, "Dota 2", invalid_elo)

    def test_insert_user_elo_given_elo_zero_then_insert_successful(self):
        valid_user_id = self.id_mocker.generate_viable_id()
        zero_elo_value = 0
        self.manager.insert_user_elo(valid_user_id, "Dota 2", zero_elo_value)
        self._assert_elo_entry_equals(valid_user_id, "Dota 2", zero_elo_value)

    def test_insert_user_elo_given_too_high_elo_then_error_raised(self):
        valid_user_id = self.id_mocker.generate_viable_id()
        too_high_elo_value = 5001
        self.assertRaises(BotBaseInternalException, self.manager.insert_user_elo, valid_user_id, "Dota 2",
                          too_high_elo_value)

    def test_insert_user_elo_given_highest_legal_elo_then_insert_successful(self):
        valid_user_id = self.id_mocker.generate_viable_id()
        highest_legal_elo = 5000
        self.manager.insert_user_elo(valid_user_id, "Dota 2", highest_legal_elo)
        self._assert_elo_entry_equals(valid_user_id, "Dota 2", highest_legal_elo)

    def test_insert_user_elo_given_invalid_game_then_error_raised(self):
        user_id = self.id_mocker.generate_viable_id()
        expected_exception = DatabaseForeignKeyViolatedException("UserElos", "Game", "not valid", "Games", "Name")
        self._assert_raises_correct_exception(expected_exception, self.manager.insert_user_elo, user_id, "not valid",
                                              1700)

    def test_add_match_given_valid_data_then_valid_id_returned(self):
        valid_match_data = self._generate_mock_match("Dota 2", 2, 5)
        self._insert_player_elos(valid_match_data[0], valid_match_data[2])
        match_id = self.manager.add_match(*valid_match_data)
        self.assertEqual(int, type(match_id))
        self.assertTrue(match_id > 0)

    def test_add_match_given_valid_data_with_no_participants_then_valid_id_returned(self):
        valid_match_data = self._generate_mock_match("Test", 0, 0)
        match_id = self.manager.add_match(*valid_match_data)
        self.assertEqual(int, type(match_id))
        self.assertTrue(match_id > 0)

    def test_fetch_match_given_valid_match_id_then_correct_data_returned(self):
        valid_match_data = self._generate_mock_match("CS:GO", 2, 5)
        valid_match_id = self._insert_match_data(valid_match_data)
        actual_match_data = self.manager.fetch_match_data(valid_match_id)
        expected_match = (valid_match_id, valid_match_data[0], valid_match_data[1])
        expected_players = valid_match_data[2]
        expected_match_data = (expected_match, expected_players)
        self.assertTupleEqual(expected_match_data, actual_match_data)

    def test_fetch_match_given_invalid_id_then_error_raised(self):
        invalid_match_id = self.id_mocker.generate_nonviable_id()
        expected_exception = DatabaseMissingRowException("Matches", "MatchID", str(invalid_match_id))
        self._assert_raises_correct_exception(expected_exception, self.manager.fetch_match_data, invalid_match_id)

    def test_change_user_elo_given_valid_positive_change_then_change_successful(self):
        valid_user_id = self.id_mocker.generate_viable_id()
        initial_elo, change = 1700, 25
        self._insert_player_elo(valid_user_id, "Dota 2", initial_elo)
        self.manager.change_user_elo(valid_user_id, "Dota 2", change)
        self._assert_user_elo_equals(valid_user_id, "Dota 2", initial_elo+change)

    def test_change_user_elo_given_valid_negative_change_then_change_successful(self):
        valid_user_id = self.id_mocker.generate_viable_id()
        initial_elo, change = 1700, -25
        self._insert_player_elo(valid_user_id, "Dota 2", initial_elo)
        self.manager.change_user_elo(valid_user_id, "Dota 2", change)
        self._assert_user_elo_equals(valid_user_id, "Dota 2", initial_elo + change)

    def test_change_user_elo_given_change_into_negative_then_zero_set_instead(self):
        valid_user_id = self.id_mocker.generate_viable_id()
        initial_elo, change = 20, -25
        self._insert_player_elo(valid_user_id, "Dota 2", initial_elo)
        self.manager.change_user_elo(valid_user_id, "Dota 2", change)
        self._assert_user_elo_equals(valid_user_id, "Dota 2", 0)

    def test_fetch_user_elo_given_valid_user_id_then_correct_elo_returned(self):
        valid_user_id = self.id_mocker.generate_viable_id()
        user_elo = 1700
        self._insert_player_elo(valid_user_id, "Dota 2", user_elo)
        self.assertEqual(user_elo, self.manager.fetch_user_elo(valid_user_id, "Dota 2"))

    def test_fetch_user_elo_given_invalid_user_id_then_error_raised(self):
        invalid_user_id = self.id_mocker.generate_nonviable_id()
        expected_exception = DatabaseMissingRowException("UserElos", "Snowflake", str(invalid_user_id))
        self._assert_raises_correct_exception(expected_exception, self.manager.fetch_user_elo, invalid_user_id,
                                              "Dota 2")

    def test_set_user_elo_given_valid_elo_value_and_existing_user_then_operation_successful(self):
        valid_user_id = self.id_mocker.generate_viable_id()
        user_elo = 2500
        self._insert_player_elo(valid_user_id, "Dota 2")
        self.manager.set_user_elo(valid_user_id, "Dota 2", user_elo)
        self._assert_user_elo_equals(valid_user_id, "Dota 2", user_elo)

    def test_set_user_elo_given_valid_elo_value_and_new_user_then_operation_successful(self):
        valid_user_id = self.id_mocker.generate_viable_id()
        user_elo = 2500
        self.manager.set_user_elo(valid_user_id, "Dota 2", user_elo)
        self._assert_user_elo_equals(valid_user_id, "Dota 2", user_elo)

    def test_set_user_elo_given_too_low_elo_value_and_new_user_then_error_raised(self):
        valid_user_id = self.id_mocker.generate_viable_id()
        user_elo = -1
        self.assertRaises(BotBaseInternalException, self.manager.set_user_elo, valid_user_id, "Dota 2", user_elo)

    def test_set_user_elo_given_too_low_elo_value_and_existing_user_then_error_raised(self):
        valid_user_id = self.id_mocker.generate_viable_id()
        user_elo = -1
        self._insert_player_elo(valid_user_id, "Dota 2")
        self.assertRaises(BotBaseInternalException, self.manager.set_user_elo, valid_user_id, "Dota 2", user_elo)

    def test_set_user_elo_given_too_high_elo_value_and_new_user_then_error_raised(self):
        valid_user_id = self.id_mocker.generate_viable_id()
        user_elo = 5001
        self.assertRaises(BotBaseInternalException, self.manager.set_user_elo, valid_user_id, "Dota 2", user_elo)

    def test_set_user_elo_given_high_elo_value_and_existing_user_then_operation_successful(self):
        valid_user_id = self.id_mocker.generate_viable_id()
        user_elo = 5001
        self._insert_player_elo(valid_user_id, "Dota 2")
        self.manager.set_user_elo(valid_user_id, "Dota 2", user_elo)
        self._assert_user_elo_equals(valid_user_id, "Dota 2", user_elo)

    def _generate_mock_game(self):
        return str(self.id_mocker.generate_viable_id()), "color", "icon", 5, 5, 2

    def _generate_mock_match(self, game: str, team_count: int, team_amount: int, *, winner=1):
        players = []
        for team in range(team_count):
            for player in range(team_amount):
                players.append((self.id_mocker.generate_viable_id(), team + 1, 1700))

        return game, winner, players

    def _assert_table_exists(self, table: str):
        with DatabaseConnectionWrapper(self.manager) as test_cursor:
            test_cursor.execute("SELECT Count(*) FROM sqlite_master WHERE type='table' AND name=?", (table,))
            self.assertEqual(test_cursor.fetchone()[0], 1, f"Expected to find table '{table}'")

    def _assert_game_exists(self, game_name: str):
        with DatabaseConnectionWrapper(self.manager) as test_cursor:
            test_cursor.execute("SELECT Count(Name) FROM Games WHERE Name=?", (game_name,))

            self.assertEqual(1, test_cursor.fetchone()[0])

    def _insert_game(self, game_data):
        with DatabaseConnectionWrapper(self.manager) as cursor:
            cursor.execute("INSERT INTO Games (Name, Colour, Icon, MinTeamSize, MaxTeamSize, TeamCount)"
                           "VALUES (?, ?, ?, ?, ?, ?)", game_data)

    def _insert_aliases(self, game, aliases):
        for alias in aliases:
            with DatabaseConnectionWrapper(self.manager) as cursor:
                cursor.execute("INSERT INTO Aliases (GameName, Alias) VALUES (?, ?)", (game, alias))

    def _fetch_aliases(self, game_name):
        with DatabaseConnectionWrapper(self.manager) as cursor:
            cursor.execute("SELECT Alias FROM Aliases WHERE GameName=?", (game_name,))
            return [row[0] for row in cursor.fetchall()]

    def _assert_tuple_is_valid_game_data(self, game_data):
        # Ignore the aliases field as it is not a primitive type
        result_message = test_utils.assert_tuple_with_correct_types(game_data[:6], str, str, str, int, int, int)
        self.assertIsNone(result_message, result_message)

    def _assert_elo_entry_equals(self, player_id: int, game: str, expected_elo: int):
        with DatabaseConnectionWrapper(self.manager) as cursor:
            cursor.execute("SELECT Elo FROM UserElos WHERE Snowflake=? AND Game=?", (player_id, game))
            self.assertEqual(expected_elo, cursor.fetchone()[0])

    def _insert_player_elos(self, game, players):
        for player in players:
            self._insert_player_elo(player[0], game, player[2])

    def _insert_player_elo(self, player_id, game, player_elo=1700):
        with DatabaseConnectionWrapper(self.manager) as cursor:
            cursor.execute("INSERT INTO UserElos(Snowflake, Game, Elo) VALUES (?, ?, ?)", (player_id, game, player_elo))

    def _insert_match_data(self, valid_match_data) -> int:
        self._insert_player_elos(valid_match_data[0], valid_match_data[2])
        match_id = self._insert_match(valid_match_data[0], valid_match_data[1])
        self._insert_participants(match_id, valid_match_data[0], valid_match_data[2])
        return match_id

    def _insert_match(self, game, winner) -> int:
        with DatabaseConnectionWrapper(self.manager) as cursor:
            cursor.execute("INSERT INTO Matches (Game, Winner) VALUES (?, ?)", (game, winner))
            return cursor.lastrowid

    def _insert_participants(self, match_id, game, participants):
        for participant in participants:
            self._insert_participant(match_id, game, participant)

    def _insert_participant(self, match_id, game, participant):
        with DatabaseConnectionWrapper(self.manager) as cursor:
            cursor.execute("INSERT INTO Participants(MatchID, Game, ParticipantID, Team, FrozenElo)"
                           "VALUES (?, ?, ?, ?, ?)", (match_id, game, *participant))

    def _assert_user_elo_equals(self, user_id, game, actual_elo):
        with DatabaseConnectionWrapper(self.manager) as cursor:
            cursor.execute("SELECT Elo FROM UserElos WHERE Snowflake=? AND Game=?", (user_id, game))
            expected_elo = cursor.fetchone()[0]
        self.assertEqual(expected_elo, actual_elo)


if __name__ == '__main__':
    unittest.main()
