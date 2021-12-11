__version__ = "ver"
__author__ = "Eetu Asikainen"

from unittest.mock import AsyncMock, MagicMock

from Bot.Cogs.ScrimCommands import ScrimCommands
from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase


class TestScrimCommands(AsyncUnittestBase):

    def setUp(self) -> None:
        self.response_builder = AsyncMock()
        self.config = MagicMock()
        self.active_scrims_manager = MagicMock()
        self.cog = ScrimCommands(self.response_builder, self.config, self.active_scrims_manager)
        self.cog._inject(MagicMock())
