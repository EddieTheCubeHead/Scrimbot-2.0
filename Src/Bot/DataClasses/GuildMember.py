__version__ = "0.1"
__author__ = "Eetu Asikainen"

import enum

from discord import Member
from sqlalchemy import Column, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship

from Bot.DataClasses.DataClass import DataClass
from Bot.DataClasses.Guild import Guild


class PermissionLevel(enum.IntEnum):
    member = 1
    moderator = 2
    admin = 3
    bot_owner = 4

    def __str__(self):
        return self.name


class GuildMember(DataClass):  # pragma: no cover
    user_id = Column(Integer, ForeignKey("Users.user_id"), primary_key=True)
    guild_id = Column(Integer, ForeignKey("Guilds.guild_id"), primary_key=True)
    bot_guild_rights_level = Column(Enum(PermissionLevel), default=PermissionLevel.member)

    user = relationship("User", back_populates="guild_memberships")

    def __init__(self, user_id: int, guild_id: int, member: Member = None):
        self.user_id = user_id
        self.guild_id = guild_id
        self.member = member
