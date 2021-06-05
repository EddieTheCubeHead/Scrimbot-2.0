__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Bot.Exceptions.BotBaseInternalException import BotBaseInternalException


# Even though database exceptions are mostly propagated to users, they are parsed into BaseUserExceptions in higher
# logic. Using BaseInternalException as a base enables possible silent tolerance and logging when necessary.
class DatabaseBaseException(BotBaseInternalException):

    def __init__(self, table: str, column: str, value: str):
        self.table = table
        self.column = column
        self.value = value

    def get_message(self) -> str:
        return f"Raw database exception in table '{self.table}', column '{self.column}' with row value '{self.value}'"
