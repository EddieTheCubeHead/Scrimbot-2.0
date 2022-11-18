from __future__ import annotations

__version__ = "0.1"
__author__ = "Eetu Asikainen"


from typing import TYPE_CHECKING

from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from hintedi import HinteDI

from Bot.Converters.Convertable import Convertable
if TYPE_CHECKING:  # pragma: no cover
    from Bot.Converters.GameConverter import GameConverter
from Bot.DataClasses.DataClass import DataClass
from Bot.DataClasses.Alias import Alias
from Bot.DataClasses.Scrim import Scrim


class Game(DataClass, Convertable):  # pragma: no cover

    name = Column(String, primary_key=True)
    _colour = Column(String, default="0xffffff")
    icon = Column(String, nullable=False)
    min_team_size = Column(Integer, nullable=False)
    max_team_size = Column(Integer, nullable=True, default=None)  # note: None = min_size, while 0 = no limit
    team_count = Column(Integer, default=2)

    # Not enums because config file is json and editable by user so enums cannot be enforced there anyways. Incorrect
    # names will default to "flat" and "mean" respectively
    rating_change_algorithm = Column(String, default="flat")
    team_rating_algorithm = Column(String, default="mean")

    aliases = relationship("Alias", back_populates="game")
    ratings = relationship("UserRating", back_populates="game")
    scrims = relationship("Scrim", back_populates="game")

    def __init__(self, name: str, colour: str, icon: str, min_team_size: int, max_team_size: int = None,
                 team_count: int = 2, aliases: list[Alias] = None, rating_change: str = "flat",
                 team_rating: str = "mean"):

        self.name = name
        self._colour = colour
        self.icon = icon
        self.aliases = aliases or []
        self.min_team_size = min_team_size
        self.max_team_size: int = max_team_size if max_team_size is not None else min_team_size
        self.team_count = team_count
        self.rating_change_algorithm = rating_change
        self.team_rating_algorithm = team_rating

    @property
    def colour(self):
        return int(self._colour, 16)

    @classmethod
    @HinteDI.inject
    def set_converter(cls, converter: GameConverter):  # pragma: no-cover
        super().set_converter(converter)
