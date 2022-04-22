from __future__ import annotations

__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import TYPE_CHECKING

from discord.ext.commands import Context

from Bot.Converters.ConverterBase import ConverterBase
from Bot.Core.BotDependencyInjector import BotDependencyInjector
if TYPE_CHECKING:  # pragma: no cover
    from Bot.DataClasses.User import User
from Database.DatabaseConnections.UserConnection import UserConnection


@BotDependencyInjector.singleton
class UserConverter(ConverterBase):

    @BotDependencyInjector.inject
    def __init__(self, connection: UserConnection):
        super().__init__(connection)

    def convert(self, ctx: Context, argument: str) -> User:
        return self.get_user(int(argument))

    def get_user(self, user_id: int) -> User:
        return self.connection.get_user(user_id)
