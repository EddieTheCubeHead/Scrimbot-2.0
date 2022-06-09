__version__ = "0.1"
__author__ = "Eetu Asikainen"


from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from Bot.DataClasses.DataClass import DataClass
from Bot.DataClasses.ParticipantTeam import ParticipantTeam


class Scrim(DataClass):  # pragma: no cover

    def __init__(self, scrim_manager):
        self.channel_id = scrim_manager.message.channel.id
        self.game_name = scrim_manager.teams_manager.game.name
        self.game = scrim_manager.teams_manager.game
        self.teams = []

    scrim_id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(Integer, ForeignKey("ScrimChannels.channel_id"), nullable=False)
    game_name = Column(String, ForeignKey("Games.name"), nullable=False)

    game = relationship("Game", back_populates="scrims")
    scrim_channel = relationship("ScrimChannel", back_populates="scrims")
    teams = relationship("ParticipantTeam", back_populates="scrim")
    results = relationship("UserScrimResult", back_populates="scrim")
