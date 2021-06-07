__version__ = "0.1"
__author__ = "Eetu Asikainen"

import sqlite3


class DatabaseConnectionWrapper:

    def __init__(self, db_manager):
        db_manager.ensure_valid_connection()
        self._connection: sqlite3.Connection = db_manager.connection
        self._cursor: sqlite3.Cursor = self._connection.cursor()

    def __enter__(self) -> sqlite3.Cursor:
        return self._cursor

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._connection.commit()
        self._cursor.close()
