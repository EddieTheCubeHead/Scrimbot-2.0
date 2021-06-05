__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import List

from Database.Exceptions.DatabaseBaseException import DatabaseBaseException


def _format_list(to_format: List[str], description):
    if len(to_format) > 1:
        return f"{description}s {', '.join(to_format[:-1])} and {to_format[-1]}"
    return f"{description} {to_format[0]}"


class DatabasePrimaryKeyViolatedException(DatabaseBaseException):

    def __init__(self, table: str, columns: List[str], values: List[str]):
        self.table = table
        self.columns = columns
        self.values = values

    def get_message(self) -> str:
        return f"Primary key consisting of {_format_list(self.values, 'value')} for " \
               f"{_format_list(self.columns, 'column')} already exists in table {self.table}"
