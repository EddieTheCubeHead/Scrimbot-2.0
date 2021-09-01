__version__ = "0.1"
__author__ = "Eetu Asikainen"


from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from Bot.DataClasses.Convertable import Convertable


class Match(Convertable):

    match_id = Column(Integer, primary_key=True, autoincrement=True)
    game_name = Column(String, ForeignKey("Games.name"), nullable=False)
    winner_team = Column(Integer, default=0)

    game = relationship("Game", back_populates="matches")
    participants = relationship("Participant", back_populates="match")
