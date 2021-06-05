__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Database.Exceptions.DatabaseBaseException import DatabaseBaseException


class DatabaseDuplicateUniqueRowException(DatabaseBaseException):

    def get_message(self) -> str:
        return f"A row with value '{self.value}' for unique restraint column '{self.column}' already exists in table " \
               f"'{self.table}'"
