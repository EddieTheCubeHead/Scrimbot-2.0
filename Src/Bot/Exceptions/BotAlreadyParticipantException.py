__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord import Member

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.Core.Logging.BotSystemLogger import BotSystemLogger
from Bot.DataClasses.Team import Team
from Bot.Exceptions.BotBaseNoContextException import BotBaseNoContextException


class BotAlreadyParticipantException(BotBaseNoContextException):

    @BotDependencyInjector.inject
    def __init__(self, member: Member, logger: BotSystemLogger):
        self.message = f"Couldn't add user <@{member.id}> to a team, because they are already participating in a scrim."
        self._logger = logger

    async def resolve(self):
        self._logger.debug(self.message)
