__version__ = "0.1"
__author__ = "Eetu Asikainen"

import sqlite3
from typing import Optional


class DatabaseConnectionWrapper:

    def __init__(self, db_file_location: str):
        self._connection: sqlite3.Connection = sqlite3.connect(db_file_location)
        self._cursor: Optional[sqlite3.Cursor] = None

    def __enter__(self) -> sqlite3.Cursor:
        self._cursor = self._connection.cursor()
        return self._cursor

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._connection.commit()
        self._cursor.close()
