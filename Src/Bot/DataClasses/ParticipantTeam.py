__version__ = "0.1"
__author__ = "Eetu Asikainen"


from sqlalchemy import Column, Integer, ForeignKey
from Bot.DataClasses.Convertable import Convertable
from Bot.DataClasses.Team import Team


class ParticipantTeam(Convertable):

    team_id = Column(Integer, ForeignKey("Teams.team_id"), primary_key=True)
    scrim_id = Column(Integer, ForeignKey("Scrims.scrim_id"), primary_key=True)
    placement = Column(Integer, default=0)
