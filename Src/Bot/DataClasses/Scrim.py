__version__ = "0.1"
__author__ = "Eetu Asikainen"


from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from Bot.DataClasses.DataClass import DataClass
from Bot.DataClasses.ParticipantTeam import ParticipantTeam


class Scrim(DataClass):

    scrim_id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(Integer, ForeignKey("ScrimChannels.channel_id"), nullable=False)
    game_name = Column(String, ForeignKey("Games.name"), nullable=False)

    game = relationship("Game", back_populates="scrims")
    scrim_channel = relationship("ScrimChannel", back_populates="scrims")
    teams = relationship("Team", secondary="ParticipantTeams", back_populates="scrims")
