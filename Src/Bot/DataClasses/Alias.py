__version__ = "0.1"
__author__ = "Eetu Asikainen"


from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

from Bot.DataClasses.DataClass import DataClass


class Alias(DataClass):
    name = Column(String, primary_key=True)
    game_name = Column(String, ForeignKey("Games.name"), nullable=False)

    game = relationship("Game", back_populates="aliases")

    def __init__(self, name: str, game_name: str):
        self.name = name
        self.game_name = game_name
