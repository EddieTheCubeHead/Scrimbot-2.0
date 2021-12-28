__version__ = "0.1"
__author__ = "Eetu Asikainen"

from logging import DEBUG

from discord import Member, Reaction

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.Core.Logging.BotSystemLogger import BotSystemLogger
from Bot.DataClasses.Team import Team
from Bot.Exceptions.BotLoggedNoContextException import BotLoggedNoContextException


class BotInvalidReactionJoinException(BotLoggedNoContextException):

    @BotDependencyInjector.inject
    def __init__(self, user: Member, team: Team, reaction: Reaction, reason: str, logger: BotSystemLogger):
        self.reaction = reaction
        self.user = user
        message = f"User '{user.id}' could not join team '{team.name}' with reaction " \
                  f"{reaction} because they are {reason}."
        super().__init__(message, logger, log=DEBUG)

    async def resolve(self):
        super().resolve()
        await self.reaction.remove(self.user)
