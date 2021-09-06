__version__ = "0.1"
__author__ = "Eetu Asikainen"


from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from Bot.DataClasses.Convertable import Convertable
from Bot.DataClasses.GuildMember import GuildMember


class User(Convertable):

    user_id = Column(Integer, primary_key=True)
    global_rights_level = Column(Integer, default=0)
    name = Column(String, nullable=False)

    guild_memberships = relationship("GuildMember", back_populates="user")
    elos = relationship("UserElo", back_populates="user")
    teams = relationship("Team", secondary="TeamMembers", back_populates="members")
