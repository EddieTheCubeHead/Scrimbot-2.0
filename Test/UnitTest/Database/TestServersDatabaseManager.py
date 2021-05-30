__version__ = "0.1"
__author__ = "Eetu Asikainen"

import unittest
import os
import shutil
import sqlite3
import json
from typing import Dict, Union, Optional

import Test.test_utils as test_utils
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

    db_folder_name: str = "TestServersDB"
    db_name: str = "servers_test.db"

    @classmethod
    def tearDownClass(cls) -> None:
        if os.path.exists(f"{cls.db_folder_name}"):
            shutil.rmtree(f"{cls.db_folder_name}")

    def setUp(self):
        self.manager = ServersDatabaseManager(self.db_folder_name, self.db_name)
        self.manager.setup_manager()

    def test_given_normal_setup_then_setup_succeeds(self):
        self.assertIn(self.db_name, os.listdir(self.manager.db_folder_path))

    def test_given_uninitialized_folder_then_folder_created(self):
        disposable_db_name = "disposed.db"
        disposable_manager = _setup_disposable_folder_manager("DisposableServersTest", disposable_db_name)
        disposable_manager.setup_manager()
        self.assertIn(disposable_db_name, os.listdir(disposable_manager.db_folder_path))

    def test_given_normal_setup_then_all_tables_initialized(self):
        for table in ("Scrims", "Servers", "ServerAdministrators"):
            self._assert_table_exists(table)

    #def test_given_valid_id_scrim_found(self):
    #    disposable_manager = _setup_disposable_folder_manager("")

    def _assert_table_exists(self, table: str):
        with DatabaseConnectionWrapper(self.manager.db_file_path) as cursor:
            cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name=?;", (table,))
            self.assertEqual(cursor.fetchone()[0], 1, f"Expected to find table '{table}'")


if __name__ == '__main__':
    unittest.main()
