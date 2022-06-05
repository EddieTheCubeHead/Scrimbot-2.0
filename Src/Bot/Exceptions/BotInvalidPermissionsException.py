__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord.ext.commands import CheckFailure

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.Core.ScrimContext import ScrimContext
from Bot.DataClasses.GuildMember import PermissionLevel
from Bot.EmbedSystem.ExceptionEmbedBuilder import ExceptionEmbedBuilder
from Bot.EmbedSystem.ScrimStates.ScrimState import ScrimState
from Bot.Exceptions.BotBaseRespondToContextException import BotBaseRespondToContextException


class BotInvalidPermissionsException(BotBaseRespondToContextException, CheckFailure):

    def __init__(self, context: ScrimContext, required_permissions: PermissionLevel,
                 actual_permissions: PermissionLevel):
        super().__init__(f"Using command '{context.command.name}' requires at least {required_permissions} level rights "
                         f"for this guild. (Your permission level: {actual_permissions})")
