__version__ = "0.1"
__author__ = "Eetu Asikainen"


from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from Bot.DataClasses.Convertable import Convertable
from Bot.DataClasses.Match import Match


class Participant(Convertable):

    user_id = Column(Integer, ForeignKey("Users.user_id"), primary_key=True)
    match_id = Column(Integer, ForeignKey("Matches.match_id"), primary_key=True)
    team = Column(Integer, default=0)
    frozen_elo = Column(Integer, nullable=True)

    user = relationship("User", back_populates="matches")
    match = relationship("Match", back_populates="participants")
