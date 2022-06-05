__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.DataClasses.GuildMember import GuildMember
from Database.DatabaseConnections.ConnectionBase import ConnectionBase


@BotDependencyInjector.singleton
class GuildMemberConnection(ConnectionBase):

    def get_guild_member(self, user_id: int, guild_id: int):
        with self._master_connection.get_session() as session:
            guild_member = session.query(GuildMember).filter(GuildMember.user_id == user_id)\
                .filter(GuildMember.guild_id == guild_id).first()
        return guild_member or self._create_guild_member(user_id, guild_id)

    def _create_guild_member(self, user_id: int, guild_id: int):
        new_guild_member = GuildMember(user_id, guild_id)
        with self._master_connection.get_session() as session:
            session.add(new_guild_member)
        return new_guild_member
