__version__ = "0.1"
__author__ = "Eetu Asikainen"

import discord

from Src.Bot.DataClasses.Game import Game

class ScrimEmbed(discord.Embed):
    def __init__(self, game: Game, is_ranked: bool):
        super().__init__(title="Status", description= "Looking for players.", color = game.colour)

        self.set_author(name=f"{game.name} {'ranked ' if is_ranked else ''}scrim", icon_url=game.icon)

        self.add_field(name="**Players**", value="_empty_", inline=True)
        self.add_field(name="**Spectators**", value="_empty_", inline=True)
        self.set_footer(text=f"To join players react \U0001F3AE To join spectators react \U0001F441")

        self._game = game

    def terminate(self, reason: str):
        self.clear_fields()
        self.description = "Scrim terminated"
        self.set_footer(text=reason)
