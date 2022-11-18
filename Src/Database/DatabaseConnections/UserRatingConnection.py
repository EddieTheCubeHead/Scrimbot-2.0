__version__ = "0.1"
__author__ = "Eetu Asikainen"

from sqlalchemy.orm import subqueryload, contains_eager, selectinload
from hintedi import HinteDI

from Bot.DataClasses.Game import Game
from Bot.DataClasses.Guild import Guild
from Bot.DataClasses.ParticipantTeam import ParticipantTeam
from Bot.DataClasses.Scrim import Scrim
from Bot.DataClasses.Team import Team
from Bot.DataClasses.User import User
from Bot.DataClasses.UserScrimResult import UserScrimResult
from Database.DatabaseConnections.ConnectionBase import ConnectionBase
from Bot.DataClasses.UserRating import UserRating


@HinteDI.singleton
class UserRatingConnection(ConnectionBase):

    def get_user_rating(self, user: User, game: Game, guild: Guild = None) -> UserRating:
        user_rating = self._try_get_user_rating(user.user_id, game.name, guild.guild_id)
        return user_rating or self._create_user_rating(user, game, guild)

    def get_user_statistics(self, user: User, game: Game, guild: Guild = None) -> UserRating:
        user_rating = self._try_get_user_statistics(user.user_id, game.name, guild.guild_id)
        return user_rating or self._create_user_rating(user, game, guild)

    def set_user_rating(self, rating: int, user: User, game: Game, guild: Guild = None) -> UserRating:
        user_rating = self._try_get_user_rating(user.user_id, game.name, guild.guild_id)
        if user_rating:
            with self._master_connection.get_session() as session:
                session.add(user_rating)
                user_rating.rating = rating
        return user_rating or self._create_user_rating(user, game, guild, rating)

    def _try_get_user_rating(self, user_id: int, game_name: str, guild_id: int = 0) -> UserRating:
        with self._master_connection.get_session() as session:
            query = session.query(UserRating).filter(UserRating.game_name == game_name)\
                .filter(UserRating.guild_id == guild_id).filter(UserRating.user_id == user_id)
            return query.first()

    def _try_get_user_statistics(self, user_id: int, game_name: str, guild_id: int = 0) -> UserRating:
        with self._master_connection.get_session() as session:
            query = session.query(UserRating)\
                .outerjoin(User).outerjoin(UserScrimResult).outerjoin(Game)\
                .filter(UserRating.game_name == game_name).filter(UserRating.guild_id == guild_id)\
                .filter(UserRating.user_id == user_id)\
                .options(selectinload(UserRating.user), selectinload(UserRating.results), selectinload(UserRating.game))
            return query.first()

    def _create_user_rating(self, user: User, game: Game, guild: Guild = None, user_rating: int = None) -> UserRating:
        guild_id = guild.guild_id if guild is not None else 0
        new_rating = UserRating(user.user_id, game.name, guild_id, user_rating)
        new_rating.user = user
        new_rating.game = game
        new_rating.guild = guild
        new_rating.results = []
        with self._master_connection.get_session() as session:
            session.add(new_rating)
        self._bind_results(new_rating)
        return new_rating

    def _bind_results(self, new_rating: UserRating):
        with self._master_connection.get_session() as session:
            query = session.query(UserScrimResult).outerjoin(UserScrimResult.scrim)\
                .filter(Scrim.game_name == new_rating.game.name)\
                .filter(UserScrimResult.user_id == new_rating.user_id)
            for result in query.all():
                new_rating.results.append(result)

