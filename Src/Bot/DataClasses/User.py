__version__ = "0.1"
__author__ = "Eetu Asikainen"


from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from Bot.DataClasses.DataClass import DataClass
from Bot.DataClasses.GuildMember import GuildMember
from Bot.DataClasses.TeamMember import TeamMember


class User(DataClass):

    user_id = Column(Integer, primary_key=True)
    global_rights_level = Column(Integer, default=0)

    guild_memberships = relationship("GuildMember", back_populates="user")
    elos = relationship("UserElo", back_populates="user")
    teams = association_proxy("member_teams", "Teams", creator=lambda team: TeamMember(team=team))

    def __init__(self, user_id: int):
        self.user_id = user_id
