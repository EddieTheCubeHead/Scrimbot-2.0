__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.DataClasses.Team import Team
from Bot.DataClasses.User import User
from Bot.EmbedSystem.ExceptionEmbedBuilder import ExceptionEmbedBuilder
from Bot.EmbedSystem.Helpers.UserNicknameService import UserNicknameService
from Bot.Exceptions.BotBaseInternalException import BotBaseInternalException


class BotInvalidPlayerRemoval(BotBaseInternalException):

    @BotDependencyInjector.inject
    def __init__(self, player: User, team: Team, nickname_service: UserNicknameService,
                 embed_builder: ExceptionEmbedBuilder):
        pass
