__version__ = "0.1"
__author__ = "Eetu Asikainen"


from sqlalchemy import Column, Integer, Boolean
from sqlalchemy.orm import relationship

from Bot.DataClasses.DataClass import DataClass
from Bot.DataClasses.Prefix import Prefix
from Configs.Config import Config


class Guild(DataClass):

    guild_id = Column(Integer, primary_key=True)
    scrim_timeout = Column(Integer, default=Config.default_timeout)
    enable_pings = Column(Boolean, default=False)
    reaction_message_id = Column(Integer, nullable=True)

    user_elos = relationship("UserElo", back_populates="guild")
    prefixes = relationship("Prefix", back_populates="guild")
    users = relationship("User", secondary="GuildMembers", viewonly=True)
    scrim_channels = relationship("ScrimChannel", back_populates="guild")
    teams = relationship("Team", back_populates="guild")
