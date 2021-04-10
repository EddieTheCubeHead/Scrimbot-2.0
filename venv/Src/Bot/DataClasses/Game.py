from __future__ import annotations


__version__ = "0.1"
__author__ = "Eetu Asikainen"


from typing import Generator, Optional


from discord.ext import commands


class Game():
    """A class that houses the data of the supported games. Might get subclassed in the future to implement FFA games.

    classmethods
    ------------
    init_games(games_data_generator)
        A classmethod that takes a generator and creates all games from the data fetched from the generator

    convert(ctx, argument)
        A classmethod implementing the discord.py converter pattern, enabling automatic converting in commands
    """

    _games_dict = {}

    def __init__(self, name: str, colour: str, icon: str, game_type: str, playercount: int, aliases: list[str]):
        """A constructor for the Game-class

        args
        ----

        :param name: The name of the game, displayed in the scrim and usable for scrim creation
        :type name: str
        :param colour: A string-form representation of the hex-code of the color associated with scrims of the game
        :type colour: str
        :param icon: A link to an icon that should be used in the scrims of the game
        :type icon: str
        :param game_type: (Functionality TBA) Whether the game is a Team-based or FFA game
        :type game_type: str
        :param playercount: The amount of players required for the game
        :type playercount: int
        :param aliases: A list of game aliases that can be used for creting scrim
        :type aliases: list[str]
        """

        self.name = name
        self.colour = int(colour, 16)
        self.playercount = playercount
        self.icon = icon
        self.type = game_type
        self.aliases = aliases

        self._games_dict[name] = self
        print(f"Created game {name}")

    @classmethod
    def init_games(cls, games_data_generator: Generator[tuple[str, str, str, str, int, list[str]], None, None]):
        """A classmethod for initializing the list of games based on a given generator.

        args
        ----

        :param games_data_generator: A generator function that yields the data for one game instance each call
        :type games_data_generator: Generator[(str, str, str, str, int, Optional[list[str]]), None, None]
        """

        while True:
            try:
                game_data = next(games_data_generator)
                Game(*game_data)
            except StopIteration:
                break

    @classmethod
    async def convert(cls, ctx: commands.Context, argument: str) -> Game:
        """A classmethod for supporting the discord.py converter pattern. Tries to convert a string to a Game instance

        args
        ----

        :param ctx: The invokation context of the command the conversion is done for
        :type ctx: commands.Context
        :param argument: The argument that should be converted into a game
        :type argument: str
        :return: A game that has a name or an alias matching the argument string
        :rtype: Game
        """

        if argument in cls._games_dict:
            return cls._games_dict[argument]
        else:
            for game in cls._games_dict:
                if argument in cls._games_dict[game].aliases:
                    return cls._games_dict[game]

        raise commands.BadArgument(f"Unrecognized game: {argument}")
