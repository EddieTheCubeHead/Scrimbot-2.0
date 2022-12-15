__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord.ext import commands
from hintedi import HinteDI

from Src.Bot.DataClasses.ScrimChannel import ScrimChannel
from Src.Bot.Logic.ActiveScrimsManager import ActiveScrimsManager


class ScrimContext(commands.Context):

    @HinteDI.inject
    def __init__(self, active_scrims_manager: ActiveScrimsManager, **kwargs):
        super().__init__(**kwargs)
        self.scrims_manager = active_scrims_manager
        self._scrim = None

    @property
    def scrim(self):
        if self._scrim is None:
            self._scrim = self.scrims_manager.try_get_scrim(self.channel.id)
        return self._scrim
