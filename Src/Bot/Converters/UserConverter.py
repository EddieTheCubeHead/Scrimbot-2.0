from __future__ import annotations

__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import TYPE_CHECKING

from discord.ext.commands import Context, converter, MemberNotFound
from hintedi import HinteDI

from Src.Bot.Converters.ConverterBase import ConverterBase
from Src.Bot.Exceptions.BotConversionFailureException import BotConversionFailureException

from Src.Bot.DataClasses.User import User
from Src.Database.DatabaseConnections.UserConnection import UserConnection


@HinteDI.singleton
class UserConverter(ConverterBase):

    connection: UserConnection

    @HinteDI.inject
    def __init__(self, connection: UserConnection):
        super().__init__(connection)

    async def convert(self, ctx: Context, argument: str) -> User:
        try:
            member = await converter.MemberConverter().convert(ctx, argument)
        except MemberNotFound:
            reason = "argument is not a valid username, nickname, user id or mention on this server"
            raise BotConversionFailureException(User.__name__, argument, reason=reason)
        user = self.get_user(member.id)
        user.member = member
        return user

    def is_in_scrim(self, user: User) -> bool:
        return self.connection.is_in_scrim(user.user_id)

    def get_user(self, user_id: int) -> User:
        return self.connection.get_user(user_id)
