__version__ = "0.1"
__author__ = "Eetu Asikainen"


from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from Bot.DataClasses.Convertable import Convertable
from Bot.Core.BotDependencyConstructor import BotDependencyConstructor
from Bot.DataClasses.Alias import Alias
from Bot.DataClasses.UserElo import UserElo


@BotDependencyConstructor.convertable
class Game(Convertable):

    name = Column(String, primary_key=True)
    colour = Column(String, default="0xffffff")
    icon = Column(String, nullable=False)
    min_team_size = Column(Integer, nullable=False)
    max_team_size = Column(Integer, nullable=True, default=None)  # note: None = min_size, while 0 = no limit
    team_count = Column(Integer, default=2)

    aliases = relationship("Alias", back_populates="game")
    elos = relationship("UserElo", back_populates="game")
    matches = relationship("Match", back_populates="game")

    def __init__(self, name: str, colour: str, icon: str, min_team_size: int, max_team_size: int = None,
                 team_count: int = 2, aliases: list[str] = None):
        """A constructor for the Game-class

        args
        ----

        :param name: The name of the game, displayed in the scrim and usable for scrim creation. Max length 32
        :type name: str
        :param colour: A string-form representation of the hex-code of the color associated with scrims of the game.
        :type colour: str
        :param icon: A link to an icon that should be used in the scrims of the game. Max length 512
        :type icon: str
        :param min_team_size: The minimum number of players a team needs
        :type min_team_size: int
        :param max_team_size: The maximum number of players a team can hold, default None results in this being equal to
        min_team_size
        :type max_team_size: Optional[int]
        :param team_count: The number of teams the game requires, default 2, 1 results in a FFA game.
        :type team_count: int
        :param aliases: A list of game aliases that can be used for creating scrim. Alias max length 32
        :type aliases: list[str]
        """

        self.name = name
        self.colour = int(colour, 16)
        self.icon = icon
        self.alias_list = aliases
        self.min_team_size = min_team_size
        self.max_team_size: int = max_team_size if max_team_size is not None else min_team_size
        self.team_count = team_count
