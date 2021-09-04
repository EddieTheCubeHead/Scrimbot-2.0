__version__ = "0.1"
__author__ = "Eetu Asikainen"


from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import relationship

from Bot.DataClasses.Convertable import Convertable


class Guild(Convertable):

    guild_id = Column(Integer, primary_key=True)
    prefix = Column(String, default="/")  # May get deprecated if bot moved to pure slash commands
    scrim_timeout = Column(Integer, default=15)
    enable_pings = Column(Boolean, default=False)
    reaction_message_id = Column(Integer, nullable=True)

    user_elos = relationship("UserElo", back_populates="guild")
    bot_rights = relationship("GuildBotRight", back_populates="guild")
    scrim_channels = relationship("ScrimChannel", back_populates="guild")
    teams = relationship("Team", back_populates="guild")
