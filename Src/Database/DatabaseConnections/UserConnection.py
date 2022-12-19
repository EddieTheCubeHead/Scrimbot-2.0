__version__ = "0.1"
__author__ = "Eetu Asikainen"

from hintedi import HinteDI

from Src.Bot.DataClasses.ParticipantTeam import ParticipantTeam
from Src.Bot.DataClasses.Scrim import Scrim, ScrimState
from Src.Bot.DataClasses.Team import Team
from Src.Bot.DataClasses.User import User
from Src.Database.DatabaseConnections.ConnectionBase import ConnectionBase


@HinteDI.singleton
class UserConnection(ConnectionBase[User]):

    def get_user(self, user_id: int) -> User:
        with self._master_connection.get_session() as session:
            query = session.query(User).filter(User.user_id == user_id)
            user = query.first()
        return user or self._create_user(user_id)

    def is_in_scrim(self, user_id: int) -> bool:
        with self._master_connection.get_session() as session:
            query = session.query(ParticipantTeam).join(ParticipantTeam.team).join(Team.members)\
                .join(ParticipantTeam.scrim).filter(Scrim.state != ScrimState.ENDED)\
                .filter(Scrim.state != ScrimState.TERMINATED)\
                .filter(User.user_id == user_id)
            active_scrim = query.first()
        return active_scrim is not None

    def is_in_another_scrim(self, user_id: int, scrim_id: int) -> bool:
        with self._master_connection.get_session() as session:
            query = session.query(ParticipantTeam).join(ParticipantTeam.team).join(Team.members)\
                .join(ParticipantTeam.scrim).filter(Scrim.state != ScrimState.ENDED)\
                .filter(Scrim.state != ScrimState.TERMINATED).filter(Scrim.scrim_id != scrim_id)\
                .filter(User.user_id == user_id)
            active_scrim = query.first()
        return active_scrim is not None

    def _create_user(self, user_id: int):
        from Src.Bot.DataClasses.User import User
        new_user = User(user_id)
        with self._master_connection.get_session() as session:
            session.add(new_user)
        return new_user
