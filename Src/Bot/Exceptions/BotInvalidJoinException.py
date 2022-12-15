__version__ = "0.1"
__author__ = "Eetu Asikainen"

from logging import DEBUG

from hintedi import HinteDI

from Src.Bot.Core.Logging.BotSystemLogger import BotSystemLogger
from Src.Bot.DataClasses.Team import Team
from Src.Bot.DataClasses.User import User
from Src.Bot.Exceptions.BotLoggedNoContextException import BotLoggedNoContextException


class BotInvalidJoinException(BotLoggedNoContextException):

    @HinteDI.inject
    def __init__(self, user: User, team: str, reason: str, logger: BotSystemLogger):
        self.user = user
        self.team = team
        self.reason = reason
        message = f"User '{user.user_id}' could not join team '{team}' because they are " \
                  f"{reason}."
        super().__init__(message, logger, log=DEBUG)
