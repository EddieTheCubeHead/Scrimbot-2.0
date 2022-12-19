__version__ = "0.1"
__author__ = "Eetu Asikainen"

from sqlalchemy.orm import subqueryload, selectinload

from hintedi import HinteDI

from Src.Database.DatabaseConnections.ConnectionBase import ConnectionBase


@HinteDI.singleton
class GuildConnection(ConnectionBase):

    def get_guild(self, guild_id: int):
        from Src.Bot.DataClasses.Guild import Guild
        with self._master_connection.get_session() as session:
            query = session.query(Guild).filter(Guild.guild_id == guild_id).outerjoin(Guild.prefixes)\
                .options(selectinload(Guild.prefixes))
            guild = query.first()
        return guild or self._create_guild(guild_id)

    def _create_guild(self, guild_id: int):
        from Src.Bot.DataClasses.Guild import Guild
        new_guild = Guild(guild_id)
        with self._master_connection.get_session() as session:
            session.add(new_guild)
        return new_guild
