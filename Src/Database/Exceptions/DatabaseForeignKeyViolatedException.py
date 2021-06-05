__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Database.Exceptions.DatabaseBaseException import DatabaseBaseException


class DatabaseForeignKeyViolatedException(DatabaseBaseException):

    def __init__(self, table, column, value, foreign_table, foreign_column):
        self.table = table
        self.column = column
        self.value = value
        self.foreign_table = foreign_table
        self.foreign_column = foreign_column

    def get_message(self) -> str:
        return f"Did not find a row in table '{self.foreign_table}' column '{self.foreign_column}' corresponding to a" \
               f" foreign key constraint with value '{self.value}' for column '{self.column}' in table '{self.table}'"
