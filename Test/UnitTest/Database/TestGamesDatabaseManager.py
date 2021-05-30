__version__ = "0.1"
__author__ = "Eetu Asikainen"

import unittest
import os
import shutil
import json
from typing import Dict, Union

import Test.test_utils as test_utils
from Src.Database.GamesDatabaseManager import GamesDatabaseManager
from Src.Database.DatabaseConnectionWrapper import DatabaseConnectionWrapper


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

    def test_given_uninitialized_folder_then_folder_created(self):
        disposable_folder = "DisposableGamesTest"
        disposable_manager = _setup_disposable_folder_manager(disposable_folder, "unused.db")
        disposable_manager.ensure_correct_folder_structure()
        self.assertIn(disposable_folder, os.listdir(disposable_manager.path))
        shutil.rmtree(disposable_manager.db_folder_path)

    def test_given_normal_setup_then_all_tables_initialized(self):
        for table in ("Games", "Aliases", "Matches", "Participants", "UserElos"):
            self._assert_table_exists(table)

    def test_given_normal_setup_then_all_games_initialized(self):
        with open(f"{self.manager.path}/games_init.json") as games_file:
            games: Dict[str, Dict[str, Union[str, int]]] = json.load(games_file)
            for game in games:
                self._assert_game_exists(game)

    def test_given_database_exists_when_games_generator_called_then_game_data_returned(self):
        games_data_generator = self.manager.games_init_generator()
        while True:
            try:
                game_data = next(games_data_generator)
                self._assert_tuple_is_valid_game_data(game_data)
            except StopIteration:
                break

    def _assert_table_exists(self, table: str):
        with DatabaseConnectionWrapper(self.manager.connection) as test_cursor:
            test_cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name=?;", (table,))
            self.assertEqual(test_cursor.fetchone()[0], 1, f"Expected to find table '{table}'")

    def _assert_game_exists(self, game_name: str):
        with DatabaseConnectionWrapper(self.manager.connection) as test_cursor:
            test_cursor.execute("SELECT Name FROM Games")

            self.assertIn(game_name, [row[0] for row in test_cursor])

    def _assert_tuple_is_valid_game_data(self, game_data):
        # Ignore the aliases field as it is not a primitive type
        result_message = test_utils.assert_tuple_with_correct_types(game_data[:6], str, str, str, int, int, int)
        self.assertIsNone(result_message, result_message)


if __name__ == '__main__':
    unittest.main()
