__version__ = "0.1"
__author__ = "Eetu Asikainen"

from sqlalchemy import Column, Integer, ForeignKey

from Bot.DataClasses.DataClass import DataClass


class TeamMember(DataClass):
    user_id = Column(Integer, ForeignKey("Users.user_id"))
    team_id = Column(Integer, ForeignKey("Teams.team_id"))
    frozen_elo = Column(Integer, nullable=False)
