__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord.ext import commands

from Bot.DataClasses.ScrimChannel import ScrimChannel


class ScrimContext(commands.Context):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._scrim = None

    async def get_scrim(self) -> ScrimChannel:
        if self._scrim:
            return self._scrim

        else:
            return await ScrimChannel.get_scrim(self)
