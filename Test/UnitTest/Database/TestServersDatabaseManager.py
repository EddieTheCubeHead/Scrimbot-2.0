__version__ = "0.1"
__author__ = "Eetu Asikainen"

import unittest
import os
import shutil
from Src.Database.ServersDatabaseManager import ServersDatabaseManager
from Src.Database.DatabaseConnectionWrapper import DatabaseConnectionWrapper


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

    def test_given_uninitialized_folder_then_folder_created(self):
        disposable_folder = "DisposableServersTest"
        disposable_manager = _setup_disposable_folder_manager(disposable_folder, "unused.db")
        disposable_manager.ensure_correct_folder_structure()
        self.assertIn(disposable_folder, os.listdir(disposable_manager.path))
        shutil.rmtree(disposable_manager.db_folder_path)

    def test_given_normal_setup_then_all_tables_initialized(self):
        for table in ("Scrims", "Servers", "ServerAdministrators"):
            self._assert_table_exists(table)

    # def test_given_valid_id_scrim_found(self):
    #     disposable_manager = _setup_disposable_folder_manager("")

    def _assert_table_exists(self, table: str):
        with DatabaseConnectionWrapper(self.manager.connection) as cursor:
            cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name=?;", (table,))
            self.assertEqual(cursor.fetchone()[0], 1, f"Expected to find table '{table}'")


if __name__ == '__main__':
    unittest.main()
