from __future__ import annotations

__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import TYPE_CHECKING

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from hintedi import HinteDI

from Src.Bot.Converters.Convertable import Convertable
from Src.Bot.DataClasses.DataClass import DataClass
from Src.Bot.DataClasses.UserScrimResult import UserScrimResult
if TYPE_CHECKING:  # pragma: no cover
    from Src.Bot.DataClasses.Game import Game
    from Src.Bot.DataClasses.Guild import Guild
    from Src.Bot.DataClasses.User import User
    from Src.Bot.Converters.UserRatingConverter import UserRatingConverter


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
    @HinteDI.inject
    def set_converter(cls, converter: UserRatingConverter):  # pragma: no cover
        super().set_converter(converter)
