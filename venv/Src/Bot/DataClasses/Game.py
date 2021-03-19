__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord.ext import commands

class Game():

    _games_dict = {}

    def __init__(self, name: str, colour: str, icon: str, game_type: str, playercount: int, aliases: list[str]):
        self.name = name
        self.colour = int(colour, 16)
        self.playercount = playercount
        self.icon = icon
        self.type = game_type
        self.aliases = aliases

        self._games_dict[name] = self
        print(f"Created game {name}")

    @classmethod
    def init_games(cls, games_data_generator):
        while True:
            try:
                game_data = next(games_data_generator)
                Game(*game_data)
            except StopIteration:
                break

    @classmethod
    async def convert(cls, ctx: commands.Context, argument: str):
        if argument in cls._games_dict:
            return cls._games_dict[argument]
        else:
            for game in cls._games_dict:
                if argument in cls._games_dict[game].aliases:
                    return cls._games_dict[game]

        raise commands.BadArgument(f"Unrecognized game: {argument}")