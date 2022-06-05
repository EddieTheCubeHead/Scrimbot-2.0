from __future__ import annotations

__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import Optional, TYPE_CHECKING

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from Bot.Converters.Convertable import Convertable
from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.DataClasses.DataClass import DataClass
from Bot.DataClasses.UserScrimResult import UserScrimResult
if TYPE_CHECKING:  # pragma: no cover
    from Bot.DataClasses.Game import Game
    from Bot.DataClasses.Guild import Guild
    from Bot.DataClasses.User import User
    from Bot.Converters.UserRatingConverter import UserRatingConverter


DEFAULT_RATING = 1700


class UserRating(DataClass, Convertable):  # pragma: no cover

    rating_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("Users.user_id"))
    guild_id = Column(Integer, ForeignKey("Guilds.guild_id"), default=0)
    game_name = Column(String, ForeignKey("Games.name"))
    rating = Column(Integer, default=DEFAULT_RATING)

    user = relationship("User", back_populates="ratings")
    game = relationship("Game", back_populates="ratings")
    guild = relationship("Guild", back_populates="user_ratings")
    results = relationship("UserScrimResult", back_populates="rating")

    def __init__(self, user_id: int, game_name: str, guild_id: int = 0, rating: int = DEFAULT_RATING):
        self.user_id = user_id
        self.game_name = game_name
        self.guild_id = guild_id
        self.rating = rating

    @classmethod
    @BotDependencyInjector.inject
    def set_converter(cls, converter: UserRatingConverter):  # pragma: no cover
        super().set_converter(converter)
