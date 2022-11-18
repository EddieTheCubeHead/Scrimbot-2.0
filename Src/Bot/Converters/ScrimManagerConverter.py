__version__ = "0.1"
__author__ = "Eetu Asikainen"

from hintedi import HinteDI

from Bot.Converters.ScrimConverter import ScrimConverter
from Bot.DataClasses.Scrim import Scrim
from Bot.Logic.ScrimManager import ScrimManager


@HinteDI.singleton
class ScrimManagerConverter:

    @HinteDI.inject
    def __init__(self, scrim_converter: ScrimConverter):
        self._converter = scrim_converter

    def wrap_scrim(self, scrim: Scrim) -> ScrimManager:
        pass
