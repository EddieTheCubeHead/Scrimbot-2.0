__version__ = "0.1"
__author__ = "Eetu Asikainen"

from sqlalchemy.orm import subqueryload, selectinload, joinedload
from hintedi import HinteDI

from Bot.DataClasses.ParticipantTeam import ParticipantTeam
from Bot.DataClasses.Scrim import Scrim, ScrimState
from Bot.DataClasses.ScrimChannel import ScrimChannel
from Bot.DataClasses.Team import Team
from Database.DatabaseConnections.ConnectionBase import ConnectionBase


@HinteDI.singleton
class ScrimConnection(ConnectionBase):

    def add_scrim(self, scrim: Scrim) -> Scrim:
        with self._master_connection.get_session() as session:
            session.add(scrim)
        return scrim

    def exists(self, channel_id: int) -> bool:
        with self._master_connection.get_session() as session:
            scrim = session.query(Scrim).filter(Scrim.channel_id == channel_id)\
                .filter(Scrim.state != ScrimState.ENDED).filter(Scrim.state != ScrimState.TERMINATED).first()
        return scrim is not None

    def get_active_scrim(self, channel_id: int) -> Scrim:
        with self._master_connection.get_session() as session:
            scrim = session.query(Scrim)\
                .filter(Scrim.state != ScrimState.ENDED).filter(Scrim.state != ScrimState.TERMINATED)\
                .filter(Scrim.channel_id == channel_id)\
                .options(selectinload(Scrim.teams).selectinload(ParticipantTeam.team).selectinload(Team.members),
                         selectinload(Scrim.game),
                         selectinload(Scrim.scrim_channel).selectinload(ScrimChannel.voice_channels))\
                .first()
        return scrim

    def edit_scrim(self, scrim: Scrim):
        with self._master_connection.get_session() as session:
            session.add(scrim)
