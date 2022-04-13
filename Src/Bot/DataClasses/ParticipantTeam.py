__version__ = "0.1"
__author__ = "Eetu Asikainen"


from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from Bot.DataClasses.DataClass import DataClass
from Bot.DataClasses.Team import Team


class ParticipantTeam(DataClass):

    team_id = Column(Integer, ForeignKey("Teams.team_id"), primary_key=True)
    scrim_id = Column(Integer, ForeignKey("Scrims.scrim_id"), primary_key=True)
    placement = Column(Integer, default=0)
    team = relationship("Team", back_populates="scrims")
    scrim = relationship("Scrim", back_populates="teams")

    def __init__(self, placement: int):
        self.placement = placement
