__version__ = "0.1"
__author__ = "Eetu Asikainen"


from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from Bot.DataClasses.Convertable import Convertable
from Bot.DataClasses.Guild import Guild


class GuildBotRight(Convertable):

    user_id = Column(Integer, ForeignKey("Users.user_id"), primary_key=True)
    guild_id = Column(Integer, ForeignKey("Guilds.guild_id"), primary_key=True)
    rights_level = Column(Integer, default=0)

    guild = relationship("Guild", back_populates="bot_rights")
    user = relationship("User", back_populates="guild_bot_rights")
