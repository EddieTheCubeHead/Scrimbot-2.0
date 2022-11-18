__version__ = "0.1"
__author__ = "Eetu Asikainen"

from logging import DEBUG

from discord import Member, Reaction
from hintedi import HinteDI

from Bot.Core.Logging.BotSystemLogger import BotSystemLogger
from Bot.DataClasses.Team import Team
from Bot.Exceptions.BotLoggedNoContextException import BotLoggedNoContextException


class BotInvalidReactionJoinException(BotLoggedNoContextException):

    @HinteDI.inject
    def __init__(self, user: Member, reaction: Reaction, message: str, logger: BotSystemLogger):
        self.reaction = reaction
        self.user = user
        super().__init__(message, logger, log=DEBUG)

    async def resolve(self):
        super().resolve()
        await self.reaction.remove(self.user)

# f"User '{user.id}' could not join team '{team.name}' with reaction {reaction} because they are {reason}."
