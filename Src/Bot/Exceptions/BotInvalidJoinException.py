__version__ = "0.1"
__author__ = "Eetu Asikainen"

from logging import DEBUG

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.Core.Logging.BotSystemLogger import BotSystemLogger
from Bot.DataClasses.Team import Team
from Bot.DataClasses.User import User
from Bot.Exceptions.BotLoggedNoContextException import BotLoggedNoContextException


class BotInvalidJoinException(BotLoggedNoContextException):

    @BotDependencyInjector.inject
    def __init__(self, user: User, team: Team, reason: str, logger: BotSystemLogger):
        self.user = user
        self.team = team
        self.reason = reason
        message = f"User '{user.user_id}' could not join team '{team.name}' because they are " \
                  f"{reason}."
        super().__init__(message, logger, log=DEBUG)
