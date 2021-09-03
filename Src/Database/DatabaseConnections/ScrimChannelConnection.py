__version__ = "0.1"
__author__ = "Eetu Asikainen"

from sqlalchemy.orm import subqueryload

from Bot.Core.BotDependencyConstructor import BotDependencyConstructor
from Bot.DataClasses.ScrimChannel import ScrimChannel
from Database.DatabaseConnections.ConnectionBase import ConnectionBase


@BotDependencyConstructor.connection
class ScrimChannelConnection(ConnectionBase[ScrimChannel]):

    def get_channel(self, channel_id: int) -> ScrimChannel:
        with self._master_connection.get_session() as session:
            session.expire_on_commit = False
            query = session.query(ScrimChannel).join(ScrimChannel.voice_channels)\
                .filter(ScrimChannel.channel_id == channel_id).options(subqueryload(ScrimChannel.voice_channels))
            channel = query.one()
        return channel

    def add_channel(self, channel: ScrimChannel):
        with self._master_connection.get_session() as session:
            session.add(channel)
