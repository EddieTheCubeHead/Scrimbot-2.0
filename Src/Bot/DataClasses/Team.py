__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import List, Optional

import discord
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from Bot.DataClasses.DataClass import DataClass
from Bot.DataClasses.TeamMember import TeamMember
from Bot.DataClasses.User import User


class Team(DataClass):

    team_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)  # TODO: when teams are more refined, create check for these two
    code = Column(String, nullable=False)  # columns should be unique per guild with global guild (id=0) considered
    guild_id = Column(Integer, ForeignKey("Guilds.guild_id"), nullable=False)
    channel_id = Column(Integer, nullable=True)  # TODO: implement check for not allowing channels on global teams

    guild = relationship("Guild", back_populates="teams")
    members = association_proxy("team_members", "user", creator=lambda user: TeamMember(user=user))
    scrims = relationship("Scrim", secondary="ParticipantTeams", back_populates="teams")

    def __init__(self, name: str, players: List[User] = None, min_size=0, max_size=0):
        """The constructor of ScrimTeam

        :param name: The name of the team
        :type name: str
        :param players: The players of the team, default None,
        :type players: List[discord.Member]
        :param min_size: The minimum size of the team for it to be considered full, default 0 (no limit)
        :type min_size: int
        :param max_size: The maximum size of the team, default 0 (no limit)
        """

        self.name = name
        self.members: List[User] = players if players is not None else []
        self.min_size: int = min_size
        self.max_size: int = max_size or min_size
        self.voice_channel: Optional[discord.VoiceChannel] = None
        self.is_pickup: bool = False
        self.winner: bool = False
        self.inline: bool = True
