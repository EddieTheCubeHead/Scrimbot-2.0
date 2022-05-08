__version__ = "ver"
__author__ = "Eetu Asikainen"

from sqlalchemy.orm import subqueryload

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Database.DatabaseConnections.ConnectionBase import ConnectionBase


@BotDependencyInjector.singleton
class GuildConnection(ConnectionBase):

    def get_guild(self, guild_id: int):
        from Bot.DataClasses.Guild import Guild
        with self._master_connection.get_session() as session:
            query = session.query(Guild).filter(Guild.guild_id == guild_id).outerjoin(Guild.prefixes)\
                .options(subqueryload(Guild.prefixes))
            guild = query.first()
        return guild or self._create_guild(guild_id)

    def _create_guild(self, guild_id: int):
        from Bot.DataClasses.Guild import Guild
        new_guild = Guild(guild_id)
        with self._master_connection.get_session() as session:
            session.add(new_guild)
        return new_guild
