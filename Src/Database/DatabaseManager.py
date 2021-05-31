__version__ = "0.1"
__author__ = "Eetu Asikainen"

import sqlite3
import os
import sys
import json
from typing import Optional, List, Tuple, Dict, Union
from abc import ABC, abstractmethod

from discord.ext import commands

from Bot.DataClasses.Game import Game
from Src.Database.DatabaseConnectionWrapper import DatabaseConnectionWrapper
from Src.Bot.Exceptions.BotBaseInternalException import BotBaseInternalException


class DatabaseManager(ABC):
    """An abstract class that serves as the base for the GamesDatabaseManager and ServersDatabaseManager.
    """

    def __init__(self, db_folder: str, db_name: str):
        self.path = os.path.join(os.path.dirname(__file__))
        self.db_folder_path: str = f"{self.path}/{db_folder}"
        self.db_file_path: str = f"{self.db_folder_path}/{db_name}"
        self.connection: Optional[sqlite3.Connection] = None

    @classmethod
    @abstractmethod
    def from_raw_file_path(cls, db_file_path: str):
        pass

    def setup_manager(self):
        # If the bot is run the first time the database needs to be initialized
        init_database = False
        if self.db_folder_path:
            init_database = self.ensure_correct_folder_structure()

        self.connection = sqlite3.connect(self.db_file_path)

        if init_database:
            self.init_database()
            self._enable_foreign_keys()

    def ensure_correct_folder_structure(self):
        init_database = not (os.path.isdir(f"{self.db_folder_path}")
                             and os.path.isfile(f"{self.db_file_path}"))
        if not os.path.exists(self.db_folder_path):
            self._init_folders()
        return init_database

    @abstractmethod
    def init_database(self):
        pass

    def _init_folders(self):
        try:
            os.mkdir(f"{self.db_folder_path}")
        except OSError:
            print(f"Error creating database folder at {self.db_folder_path}; shutting down.")
            sys.exit(1)

    def _create_tables(self, *table_names: str):
        with DatabaseConnectionWrapper(self.connection) as db_cursor:
            for table in table_names:
                self._run_script(f"Create{table}Table.sql", db_cursor)

    def _run_script(self, script: str, cursor: sqlite3.Cursor):
        with open(f"{self.path}/SQLScripts/{script}") as script:
            cursor.execute(script.read())

    def _ensure_valid_connection(self):
        if self.connection is None:
            raise BotBaseInternalException(f"Tried to use database in {self.db_file_path} before the connection was "
                                           f"set up.")

    def set_player_elo(self, player_id: int, elo: int, game: Game):
        """A method that updates a player's elo in the table or creates a new record if the player has no elo

        :param player_id: The discord id ("snowflake") of the player whose elo should be updated
        :type player_id: int
        :param elo: The new elo value of the player
        :type elo: int
        :param game: The game
        :type game:
        """

    def _enable_foreign_keys(self):
        with DatabaseConnectionWrapper(self.connection) as cursor:
            cursor.execute("PRAGMA foreign_keys = ON")
