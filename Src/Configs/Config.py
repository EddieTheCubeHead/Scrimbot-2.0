__version__ = "0.1"
__author__ = "Eetu Asikainen"

import json
import os


class _Config:

    @property
    def games_dict(self) -> dict:
        with open(os.path.join(os.path.dirname(__file__), "games_init.json"), encoding="utf-8") as games:
            games_dict = json.load(games)
        return games_dict


Config = _Config()
