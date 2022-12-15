__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord import Member
from hintedi import HinteDI

from Src.Bot.Core.Logging.BotSystemLogger import BotSystemLogger
from Src.Bot.DataClasses.Team import Team
from Src.Bot.Exceptions.BotBaseNoContextException import BotBaseNoContextException


class BotAlreadyParticipantException(BotBaseNoContextException):

    @HinteDI.inject
    def __init__(self, member: Member, logger: BotSystemLogger):
        self.message = f"Couldn't add user <@{member.id}> to a team, because they are already participating in a scrim."
        self._logger = logger

    async def resolve(self):
        self._logger.debug(self.message)
