from __future__ import annotations

__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import TYPE_CHECKING, Optional

import discord
from sqlalchemy import Column, Integer, Boolean
from sqlalchemy.orm import relationship
from hintedi import HinteDI

from Src.Bot.Converters.Convertable import Convertable
from Src.Bot.DataClasses.DataClass import DataClass
from Configs.Config import Config
from Src.Bot.DataClasses.Prefix import Prefix
from Src.Bot.DataClasses.UserRating import UserRating
if TYPE_CHECKING:  # pragma: no cover
    from Src.Bot.Converters.GuildConverter import GuildConverter


class Guild(DataClass, Convertable):  # pragma: no cover

    guild_id = Column(Integer, primary_key=True)
    scrim_timeout = Column(Integer, default=Config().default_timeout)
    enable_pings = Column(Boolean, default=False)
    reaction_message_id = Column(Integer, nullable=True)

    user_ratings = relationship("UserRating", back_populates="guild")
    prefixes = relationship("Prefix", back_populates="guild")
    users = relationship("User", secondary="GuildMembers", viewonly=True)
    scrim_channels = relationship("ScrimChannel", back_populates="guild")
    teams = relationship("Team", back_populates="guild")

    def __init__(self, guild_id: int, prefixes: Optional[list[Prefix]] = None):
        self.guild_id = guild_id
        if prefixes is not None:
            self.prefixes = prefixes
        else:
            self.prefixes = []

    @classmethod
    @HinteDI.inject
    def set_converter(cls, converter: GuildConverter):
        super().set_converter(converter)
