__version__ = "0.1"
__author__ = "Eetu Asikainen"


from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from Bot.DataClasses.Convertable import Convertable
from Bot.DataClasses.User import User


_DEFAULT_ELO = 1700


class UserElo(Convertable):

    user_id = Column(Integer, ForeignKey("Users.user_id"), primary_key=True)
    guild_id = Column(Integer, ForeignKey("Guilds.guild_id"), primary_key=True, default=0)
    game_name = Column(String, ForeignKey("Games.name"), primary_key=True)
    elo = Column(Integer, default=_DEFAULT_ELO)

    user = relationship("User", back_populates="elos")
    guild = relationship("Guild", back_populates="user_elos")
    game = relationship("Game", back_populates="elos")
