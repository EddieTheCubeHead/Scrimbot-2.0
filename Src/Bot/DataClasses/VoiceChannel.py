from __future__ import annotations

__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import Optional, TYPE_CHECKING

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from hintedi import HinteDI

from Bot.Converters.Convertable import Convertable

if TYPE_CHECKING:  # pragma: no cover
    from Bot.Converters.VoiceChannelConverter import VoiceChannelConverter
from Bot.DataClasses.DataClass import DataClass


class VoiceChannel(DataClass, Convertable):  # pragma: no cover

    channel_id = Column(Integer, primary_key=True)
    parent_channel_id = Column(Integer, ForeignKey("ScrimChannels.channel_id"), nullable=False)
    team_number = Column(Integer, nullable=False)

    parent_channel = relationship("ScrimChannel", back_populates="voice_channels", lazy="joined")
    teams = relationship("Team", back_populates="voice_channel")

    def __init__(self, channel_id: int, parent_channel_id: int, team_number: int = None):
        self.channel_id: int = channel_id
        self.parent_channel_id: int = parent_channel_id
        self.team_number: Optional[int] = team_number

    @classmethod
    @HinteDI.inject
    def set_converter(cls, converter: VoiceChannelConverter):
        super().set_converter(converter)
