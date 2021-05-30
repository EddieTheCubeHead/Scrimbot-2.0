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
from Src.Database.DatabaseManager import DatabaseManager
from Src.Database.DatabaseConnectionWrapper import DatabaseConnectionWrapper


def _insert_game(cursor: sqlite3.Cursor, game: Dict[str, Union[str, int]], game_name: str):
    max_team_size = game["max_team_size"] if "max_team_size" in game else game["min_team_size"]
    team_count = 2 if "team_count" not in game else game["team_count"]
    cursor.execute("""INSERT INTO Games (Name, Colour, Icon, MinTeamSize, MaxTeamSize, TeamCount) VALUES
                         (?, ?, ?, ?, ?, ?)""",
                         (game_name, game['colour'], game['icon'], game['min_team_size'], max_team_size,
                          team_count))

    for alias in game['alias']:
        cursor.execute("INSERT INTO Aliases (GameName, Alias) VALUES (?, ?)",
                       (game_name, alias))


class GamesDatabaseManager(DatabaseManager):

    def __init__(self, db_folder: str = "DBFiles", db_file: str = "games.db"):
        super().__init__(db_folder, db_file)

    @classmethod
    def from_raw_file_path(cls, db_file_path: str):
        new_manager = cls("", "")
        new_manager.db_file_path = db_file_path
        return new_manager

    def init_database(self):
        super()._ensure_valid_connection()
        self._create_tables("Games", "Aliases", "Matches", "Participants", "UserElos")

        with open(f"{self.path}/games_init.json") as games_file:
            games: Dict[str, Dict[str, Union[str, int]]] = json.load(games_file)

        with DatabaseConnectionWrapper(self.connection) as cursor:
            for game in games:
                _insert_game(cursor, games[game], game)

    def games_init_generator(self) -> Tuple[str, str, str, int, int, int, List[str]]:
        """A generator that yields the data of all games stored in the database, one game per iteration.

        :return: A tuple containing all the data required in the Game constructor
        :rtype: tuple[str, str, str, str, int, Optional[list[str]]]
        """

        with DatabaseConnectionWrapper(self.connection) as cursor:

            cursor.execute("SELECT * FROM Games")
            game_rows = cursor.fetchall()

            for game in game_rows:
                cursor.execute("SELECT Alias FROM Aliases WHERE GameName = ?", (game[0],))
                aliases = [alias[0] for alias in cursor.fetchall()]

                yield *game, aliases


# Enable initializing the database without starting the bot by making this file executable and running the
# initialization logic on execution
if __name__ == "__main__":
    init_manager = GamesDatabaseManager()
    init_manager.setup_manager()
