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


class ServersDatabaseManager(DatabaseManager):

    def __init__(self, db_folder: str = "DBFiles", db_file: str = "servers.db"):
        super().__init__(db_folder, db_file)

    def init_database(self):
        super()._create_tables("Scrims", "Servers", "ServerAdministrators")
