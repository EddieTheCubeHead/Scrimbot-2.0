__version__ = "0.1"
__author__ = "Eetu Asikainen"

from sqlalchemy.orm import subqueryload

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.DataClasses.ParticipantTeam import ParticipantTeam
from Bot.DataClasses.Scrim import Scrim, ScrimState
from Bot.DataClasses.Team import Team
from Database.DatabaseConnections.ConnectionBase import ConnectionBase


@BotDependencyInjector.singleton
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
            scrim = session.query(Scrim).filter(Scrim.channel_id == channel_id)\
                .outerjoin(Scrim.game).outerjoin(Scrim.teams).outerjoin(ParticipantTeam.team).outerjoin(Team.members)\
                .filter(Scrim.state != ScrimState.ENDED).filter(Scrim.state != ScrimState.TERMINATED)\
                .options(subqueryload(Scrim.game),
                         subqueryload(Scrim.teams),
                         subqueryload(Scrim.teams, ParticipantTeam.team, Team.members))\
                .first()
        return scrim
