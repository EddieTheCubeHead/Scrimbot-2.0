__version__ = "ver"
__author__ = "Eetu Asikainen"

from sqlalchemy.orm import subqueryload, contains_eager

from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.DataClasses.Game import Game
from Bot.DataClasses.Guild import Guild
from Bot.DataClasses.ParticipantTeam import ParticipantTeam
from Bot.DataClasses.Scrim import Scrim
from Bot.DataClasses.Team import Team
from Bot.DataClasses.User import User
from Database.DatabaseConnections.ConnectionBase import ConnectionBase
from Bot.DataClasses.UserRating import UserRating


@BotDependencyInjector.singleton
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
                .outerjoin(User).outerjoin(User.teams).outerjoin(Team.scrims)\
                .filter(UserRating.game_name == game_name).filter(UserRating.guild_id == guild_id)\
                .filter(UserRating.user_id == user_id)\
                .options(subqueryload(UserRating.user), subqueryload(UserRating.user, User.teams),
                         subqueryload(UserRating.user, User.teams, Team.scrims))
            return query.first()

    def _create_user_rating(self, user: User, game: Game, guild: Guild = None, user_rating: int = None) -> UserRating:
        guild_id = guild.guild_id if guild is not None else 0
        new_rating = UserRating(user.user_id, game.name, guild_id, user_rating)
        new_rating.user = user
        new_rating.game = game
        new_rating.guild = guild
        with self._master_connection.get_session() as session:
            session.add(new_rating)
        return new_rating

