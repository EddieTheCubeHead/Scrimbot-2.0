__version__ = "0.1"
__author__ = "Eetu Asikainen"

from logging import DEBUG

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.Core.Logging.BotSystemLogger import BotSystemLogger
from Bot.DataClasses.Team import Team
from Bot.DataClasses.User import User
from Bot.Exceptions.BotBaseInternalSystemException import BotBaseInternalSystemException


def _construct_message(player: User, team: Team) -> str:
    return f"Tried to remove player <@{player.user_id}> from team '{team.name}' even though they are not a team " \
           f"member."


class BotInvalidPlayerRemoval(BotBaseInternalSystemException):

    @BotDependencyInjector.inject
    def __init__(self, player: User, team: Team, logger: BotSystemLogger):
        self.message = _construct_message(player, team)
        super().__init__(self.message, logger, log=DEBUG)
