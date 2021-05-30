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


class ServersDatabaseManager(DatabaseManager):

    def __init__(self, db_folder: str = "DBFiles", db_file: str = "servers.db"):
        super().__init__(db_folder, db_file)

    @classmethod
    def from_raw_file_path(cls, db_file_path: str):
        new_manager = cls("", "")
        new_manager.db_file_path = db_file_path
        return new_manager

    def init_database(self):
        super()._create_tables("Scrims", "Servers", "ServerAdministrators")

    def fetch_scrim(self, channel_id: int) -> Optional[Tuple]:
        """A method for fetching a row containing the data of a specified scrim from the database

        args
        ----

        :param channel_id: The unique discord id of the channel of which to fetch scrim data of
        :type channel_id: int
        :return: An sqlite row-object of the data
        :rtype: Optional[sqlite3.Row]
        """

        with DatabaseConnectionWrapper(self.connection) as cursor:
            cursor.execute("SELECT * FROM Scrims WHERE ChannelID = ?", (channel_id,))
            scrim_row = cursor.fetchone()

        return scrim_row
