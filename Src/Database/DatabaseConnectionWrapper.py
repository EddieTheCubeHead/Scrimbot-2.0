__version__ = "0.1"
__author__ = "Eetu Asikainen"

import sqlite3
from typing import Optional


class DatabaseConnectionWrapper:

    def __init__(self, db_connection: sqlite3.Connection):
        self._connection: sqlite3.Connection = db_connection
        self._cursor: sqlite3.Cursor = db_connection.cursor()

    def __enter__(self) -> sqlite3.Cursor:
        return self._cursor

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._connection.commit()
        self._cursor.close()
