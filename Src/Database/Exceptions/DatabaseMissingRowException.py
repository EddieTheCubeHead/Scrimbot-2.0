__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Database.Exceptions.DatabaseBaseException import DatabaseBaseException


class DatabaseMissingRowException(DatabaseBaseException):

    def get_message(self) -> str:
        return f"Did not find a row with value '{self.value}' for column '{self.column}' in table '{self.table}'"
