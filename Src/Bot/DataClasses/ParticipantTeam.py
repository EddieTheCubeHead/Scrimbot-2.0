__version__ = "0.1"
__author__ = "Eetu Asikainen"


from sqlalchemy import Column, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from Bot.DataClasses.DataClass import DataClass
from Bot.DataClasses.Team import Team


class ParticipantTeam(DataClass):  # pragma: no cover

    team_id = Column(Integer, ForeignKey("Teams.team_id"), primary_key=True)
    scrim_id = Column(Integer, ForeignKey("Scrims.scrim_id"), primary_key=True)
    tied = Column(Boolean, default=False)
    placement = Column(Integer, default=0, nullable=True)
    max_size = Column(Integer, default=0)
    min_size = Column(Integer, default=0)
    team = relationship("Team", back_populates="scrims")
    scrim = relationship("Scrim", back_populates="teams")

    def __init__(self, placement: int | None, max_size: int = 0, min_size: int = None):
        self.placement = placement
        self.max_size = max_size
        self.min_size = min_size if min_size is not None else max_size
