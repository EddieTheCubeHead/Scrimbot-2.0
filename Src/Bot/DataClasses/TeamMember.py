__version__ = "0.1"
__author__ = "Eetu Asikainen"


from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from Src.Bot.DataClasses.DataClass import DataClass


class TeamMember(DataClass):  # pragma: no cover

    user_id = Column(Integer, ForeignKey("Users.user_id"), primary_key=True)
    team_id = Column(Integer, ForeignKey("Teams.team_id"), primary_key=True)

    def __init__(self, user=None, team=None):
        self.user = user
        self.team = team
