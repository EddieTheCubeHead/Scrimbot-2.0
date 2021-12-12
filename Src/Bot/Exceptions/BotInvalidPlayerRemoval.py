__version__ = "0.1"
__author__ = "Eetu Asikainen"

from logging import DEBUG

from discord.ext.commands import Context

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.Core.ScrimBotLogger import ScrimBotLogger
from Bot.DataClasses.Team import Team
from Bot.DataClasses.User import User
from Bot.EmbedSystem.Helpers.UserNicknameService import UserNicknameService
from Bot.Exceptions.BotBaseInternalException import BotBaseInternalException


class BotInvalidPlayerRemoval(BotBaseInternalException):

    @BotDependencyInjector.inject
    def __init__(self, ctx: Context, player: User, team: Team, nickname_service: UserNicknameService,
                 logger: ScrimBotLogger):
        self.nickname_service = nickname_service
        self.message = self._construct_message(ctx, player, team)
        super().__init__(self.message, logger, log=DEBUG)

    def _construct_message(self, ctx: Context, player: User, team: Team) -> str:
        return f"Tried to remove player '{self.nickname_service.get_name(ctx, player.user_id)}' from team " \
               f"'{team.name}' even though they are not a team member."
