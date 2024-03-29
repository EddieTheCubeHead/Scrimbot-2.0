__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord.ext.commands import converter

from Bot.Converters.ConverterBase import ConverterBase
from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.Core.ScrimContext import ScrimContext
from Bot.DataClasses.GuildMember import GuildMember
from Database.DatabaseConnections.GuildMemberConnection import GuildMemberConnection


@BotDependencyInjector.singleton
class GuildMemberConverter(ConverterBase):

    connection: GuildMemberConnection

    @BotDependencyInjector.inject
    def __init__(self, connection: GuildMemberConnection):
        super().__init__(connection)

    async def convert(self, ctx: ScrimContext, argument: str) -> GuildMember:
        member = await converter.MemberConverter().convert(ctx, argument)
        user = self.get_guild_member(member.id, ctx.guild.id)
        user.member = member
        return user

    def get_guild_member(self, user_id: int, guild_id: int) -> GuildMember:
        return self.connection.get_guild_member(user_id, guild_id)
