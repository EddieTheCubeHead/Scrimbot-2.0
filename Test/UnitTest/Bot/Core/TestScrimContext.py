__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Bot.Core.ScrimContext import ScrimContext
from Bot.Logic.ScrimManager import ScrimManager
from Test.Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase
from Test.Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestScrimContext(AsyncUnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()

    def setUp(self) -> None:
        self.active_scrims_manager = MagicMock()
        self.scrims = {}
        self.active_scrims_manager.try_get_scrim.side_effect = lambda x: self.scrims[x] if x in self.scrims else None
        self.channel = MagicMock()
        message = MagicMock()
        message.channel = self.channel
        self.context = ScrimContext(self.active_scrims_manager, message=message, prefix=";")

    async def test_scrim_property_given_channel_id_not_in_active_scrims_manager_then_none_returned(self):
        self.channel.id = self.id_generator.generate_viable_id()
        self.assertIsNone(self.context.scrim)

    def _create_scrim(self, channel_id: int) -> ScrimManager:
        scrim = MagicMock()
        self.scrims[channel_id] = scrim
        return scrim
