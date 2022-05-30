from __future__ import annotations

__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import TYPE_CHECKING

from discord import Member
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from Bot.Converters.Convertable import Convertable
if TYPE_CHECKING:  # pragma: no cover
    from Bot.Converters.UserConverter import UserConverter
from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.DataClasses.DataClass import DataClass
from Bot.DataClasses.GuildMember import GuildMember
from Bot.DataClasses.TeamMember import TeamMember


class User(DataClass, Convertable):  # pragma: no cover

    user_id = Column(Integer, primary_key=True)
    global_rights_level = Column(Integer, default=0)

    guild_memberships = relationship("GuildMember", back_populates="user")
    elos = relationship("UserRating", back_populates="user")
    teams = relationship("Team", secondary=TeamMember.__table__, back_populates="members")

    def __init__(self, user_id: int, member: Member = None):
        self.user_id = user_id
        self.member = member

    @classmethod
    @BotDependencyInjector.inject
    def set_converter(cls, converter: UserConverter):
        super().set_converter(converter)
