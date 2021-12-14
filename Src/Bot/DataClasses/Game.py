from __future__ import annotations

__version__ = "0.1"
__author__ = "Eetu Asikainen"


from typing import TYPE_CHECKING

from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

if TYPE_CHECKING:
    from Bot.Converters.GameConverter import GameConverter
from Bot.DataClasses.DataClass import DataClass
from Bot.Core.BotDependencyInjector import BotDependencyInjector
from Bot.DataClasses.Alias import Alias
from Bot.DataClasses.UserElo import UserElo
from Bot.DataClasses.Scrim import Scrim


class Game(DataClass):

    name = Column(String, primary_key=True)
    _colour = Column(String, default="0xffffff")
    icon = Column(String, nullable=False)
    min_team_size = Column(Integer, nullable=False)
    max_team_size = Column(Integer, nullable=True, default=None)  # note: None = min_size, while 0 = no limit
    team_count = Column(Integer, default=2)

    aliases = relationship("Alias", back_populates="game")
    elos = relationship("UserElo", back_populates="game")
    scrims = relationship("Scrim", back_populates="game")

    def __init__(self, name: str, colour: str, icon: str, min_team_size: int, max_team_size: int = None,
                 team_count: int = 2, aliases: list[Alias] = None):

        self.name = name
        self._colour = colour
        self.icon = icon
        self.aliases = aliases or []
        self.min_team_size = min_team_size
        self.max_team_size: int = max_team_size if max_team_size is not None else min_team_size
        self.team_count = team_count

    @property
    def colour(self):
        return int(self._colour, 16)

    @classmethod
    @BotDependencyInjector.inject
    def set_converter(cls, converter: GameConverter):  # pragma: no-cover
        super().set_converter(converter)
