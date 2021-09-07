__version__ = "0.1"
__author__ = "Eetu Asikainen"

from sqlalchemy.orm import subqueryload

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.DataClasses.ScrimChannel import ScrimChannel
from Database.DatabaseConnections.ConnectionBase import ConnectionBase


@BotDependencyInjector.singleton
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
