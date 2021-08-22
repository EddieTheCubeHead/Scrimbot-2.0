__version__ = "0.1"
__author__ = "Eetu Asikainen"


from typing import List

from Bot.Converters.Convertable import Convertable
from Bot.Core.ConvertableConstructor import ConvertableConstructor


@ConvertableConstructor.convertable
class Game(Convertable):

    def __init__(self, name: str, colour: str, icon: str, min_team_size: int, max_team_size: int = None,
                 team_count: int = 2, aliases: List[str] = None):
        """A constructor for the Game-class

        args
        ----

        :param name: The name of the game, displayed in the scrim and usable for scrim creation
        :type name: str
        :param colour: A string-form representation of the hex-code of the color associated with scrims of the game
        :type colour: str
        :param icon: A link to an icon that should be used in the scrims of the game
        :type icon: str
        :param min_team_size: The minimum number of players a team needs
        :type min_team_size: int
        :param max_team_size: The maximum number of players a team can hold, default None results in this being equal to
        min_team_size
        :type max_team_size: Optional[int]
        :param team_count: The number of teams the game requires, default 2, 1 results in a FFA game.
        :type team_count: int
        :param aliases: A list of game aliases that can be used for creating scrim
        :type aliases: List[str]
        """

        self.name = name
        self.colour = int(colour, 16)
        self.icon = icon
        self.aliases = aliases
        self.min_team_size = min_team_size
        self.max_team_size: int = max_team_size if max_team_size is not None else min_team_size
        self.team_count = team_count
