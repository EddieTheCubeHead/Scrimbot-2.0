__version__ = "0.1"
__author__ = "Eetu Asikainen"


from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship

from Bot.DataClasses.Convertable import Convertable
from Bot.DataClasses.Guild import Guild


class GuildMember(Convertable):

    user_id = Column(Integer, ForeignKey("Users.user_id"), primary_key=True)
    guild_id = Column(Integer, ForeignKey("Guilds.guild_id"), primary_key=True)
    bot_guild_rights_level = Column(Integer, default=0)
    nickname = Column(String, nullable=True)

    user = relationship("User", back_populates="guild_memberships")
