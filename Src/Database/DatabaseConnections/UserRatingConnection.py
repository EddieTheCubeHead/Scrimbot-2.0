__version__ = "ver"
__author__ = "Eetu Asikainen"

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Database.DatabaseConnections.ConnectionBase import ConnectionBase
from Bot.DataClasses.UserRating import UserRating


@BotDependencyInjector.singleton
class UserRatingConnection(ConnectionBase):

    def get_user_rating(self, user_id: int, game_name: str, guild_id: int = 0) -> UserRating:
        user_rating = self._try_get_user_rating(user_id, game_name, guild_id)
        return user_rating or self._create_user_rating(user_id, game_name, guild_id)

    def _try_get_user_rating(self, user_id: int, game_name: str, guild_id: int = 0) -> UserRating:
        with self._master_connection.get_session() as session:
            query = session.query(UserRating).filter(UserRating.user_id == user_id)\
                .filter(UserRating.game_name == game_name).filter(UserRating.guild_id == guild_id)
            return query.first()

    def _create_user_rating(self, user_id: int, game_name: str, guild_id: int, user_rating: int = None) -> UserRating:
        new_rating = UserRating(user_id, game_name, guild_id, user_rating)
        with self._master_connection.get_session() as session:
            session.add(new_rating)
        return new_rating

    def set_user_rating(self, rating: int, user_id: int, game_name: str, guild_id: int = 0):
        user_rating = self._try_get_user_rating(user_id, game_name, guild_id)
        if user_rating:
            with self._master_connection.get_session() as session:
                session.add(user_rating)
                user_rating.rating = rating
        return user_rating or self._create_user_rating(user_id, game_name, guild_id, rating)

