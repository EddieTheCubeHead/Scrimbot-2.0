from __future__ import annotations

__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import Optional, TYPE_CHECKING

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

if TYPE_CHECKING:
    from Bot.Converters.VoiceChannelConverter import VoiceChannelConverter
from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.DataClasses.DataClass import DataClass


class VoiceChannel(DataClass):

    channel_id = Column(Integer, primary_key=True)
    parent_channel_id = Column(Integer, ForeignKey("ScrimChannels.channel_id"), nullable=False)
    team = Column(Integer, nullable=False)

    parent_channel = relationship("ScrimChannel", back_populates="voice_channels")

    def __init__(self, channel_id: int, parent_channel_id: int, team: int = None):
        self.channel_id: int = channel_id
        self.parent_channel_id: int = parent_channel_id
        self.team: Optional[int] = team

    @classmethod
    @BotDependencyInjector.inject
    def set_converter(cls, converter: VoiceChannelConverter):  # pragma: no cover
        super().set_converter(converter)
