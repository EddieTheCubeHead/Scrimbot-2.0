__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import Union, Optional

from sqlalchemy.orm import subqueryload, selectinload
from hintedi import HinteDI

from Src.Bot.DataClasses.ScrimChannel import ScrimChannel
from Src.Bot.DataClasses.VoiceChannel import VoiceChannel
from Database.DatabaseConnections.ConnectionBase import ConnectionBase


def _get_from_id(channel_id, session):
    query = session.query(ScrimChannel).outerjoin(ScrimChannel.voice_channels) \
        .filter(ScrimChannel.channel_id == channel_id).options(subqueryload(ScrimChannel.voice_channels))
    return query


@HinteDI.singleton
class ScrimChannelConnection(ConnectionBase[ScrimChannel]):

    def get_channel(self, channel_id: int) -> ScrimChannel:
        with self._master_connection.get_session() as session:
            query = _get_from_id(channel_id, session)
            channel = query.one()
        return channel

    def add_channel(self, channel: ScrimChannel) -> ScrimChannel:
        with self._master_connection.get_session() as session:
            session.add(channel)
        return channel

    def exists_text(self, channel_id: int) -> Optional[ScrimChannel]:
        with self._master_connection.get_session() as session:
            candidate = _get_from_id(channel_id, session).first()
        return candidate

    def exists_voice(self, channel_id: int) -> Optional[ScrimChannel]:
        with self._master_connection.get_session() as session:
            return session.query(ScrimChannel).join(ScrimChannel.voice_channels)\
                .filter(VoiceChannel.channel_id == channel_id)\
                .options(selectinload(ScrimChannel.voice_channels)).first()
