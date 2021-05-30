__version__ = "0.1"
__author__ = "Eetu Asikainen"

import unittest
import os
import shutil
from typing import Tuple, Optional

import test_utils
from Src.Database.ServersDatabaseManager import ServersDatabaseManager
from Src.Database.DatabaseConnectionWrapper import DatabaseConnectionWrapper
import Test.test_utils


def _setup_disposable_folder_manager(disposable_folder_name: str, disposable_file_name: str) -> \
        ServersDatabaseManager:
    if not disposable_folder_name:
        raise Exception("Passing null string into setup disposable folder manager!")
    disposable_folder_manager = ServersDatabaseManager(disposable_folder_name, disposable_file_name)
    if os.path.exists(disposable_folder_manager.db_folder_path):
        shutil.rmtree(disposable_folder_manager.db_folder_path)

    return disposable_folder_manager


class TestServersDatabaseManager(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.manager: ServersDatabaseManager = ServersDatabaseManager.from_raw_file_path(":memory:")
        cls.manager.setup_manager()
        cls.IDMocker = test_utils.UniqueIdGenerator()

    def test_given_uninitialized_folder_then_folder_created(self):
        disposable_folder = "DisposableServersTest"
        disposable_manager = _setup_disposable_folder_manager(disposable_folder, "unused.db")
        disposable_manager.ensure_correct_folder_structure()
        self.assertIn(disposable_folder, os.listdir(disposable_manager.path))
        shutil.rmtree(disposable_manager.db_folder_path)

    def test_given_normal_setup_then_all_tables_initialized(self):
        for table in ("Scrims", "Servers", "ServerAdministrators"):
            self._assert_table_exists(table)

    def test_given_valid_id_scrim_found(self):
        expected_ids = self.IDMocker.generate_viable_id_group(4)
        self._insert_test_ids(expected_ids)
        actual_ids = self.manager.fetch_scrim(expected_ids[0])
        self.assertTupleEqual(expected_ids, actual_ids)

    def _assert_table_exists(self, table: str):
        with DatabaseConnectionWrapper(self.manager.connection) as cursor:
            cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name=?;", (table,))
            self.assertEqual(cursor.fetchone()[0], 1, f"Expected to find table '{table}'")

    def _insert_test_ids(self, *channel_id_groups: Tuple[int, Optional[int], Optional[int], Optional[int]]):
        for id_group in channel_id_groups:
            with DatabaseConnectionWrapper(self.manager.connection) as cursor:
                cursor.execute("INSERT INTO Scrims (ChannelID, Team1VoiceID, Team2VoiceID, SpectatorVoiceID) \
                                VALUES (?, ?, ?, ?)", id_group)


if __name__ == '__main__':
    unittest.main()
