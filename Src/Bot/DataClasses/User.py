__version__ = "0.1"
__author__ = "Eetu Asikainen"


from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import relationship

from Bot.DataClasses.Convertable import Convertable
from Bot.DataClasses.GuildBotRight import GuildBotRight
from Bot.DataClasses.Participant import Participant


class User(Convertable):

    user_id = Column(Integer, primary_key=True)
    global_rights_level = Column(Integer, default=0)

    guild_bot_rights = relationship("GuildBotRight", back_populates="user")
    elos = relationship("UserElo", back_populates="user")
    matches = relationship("Participant", back_populates="user")
