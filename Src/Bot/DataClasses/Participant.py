__version__ = "0.1"
__author__ = "Eetu Asikainen"


from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from Bot.DataClasses.Convertable import Convertable


class Participant(Convertable):

    user_id = Column(Integer, ForeignKey("Users.user_id"), primary_key=True)
    scrim_id = Column(Integer, ForeignKey("Scrims.match_id"), primary_key=True)
    team = Column(Integer, default=0)
    frozen_elo = Column(Integer, nullable=True)

    user = relationship("User", back_populates="matches")
    scrim = relationship("Scrim", back_populates="participants")
