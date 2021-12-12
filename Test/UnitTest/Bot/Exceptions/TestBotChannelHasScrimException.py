__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Bot.Exceptions.BotChannelHasScrimException import BotChannelHasScrimException
from Utils.TestBases.UnittestBase import UnittestBase
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestBotChannelHasScrimException(UnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()

    def test_init_given_channel_id_then_message_with_channel_mention_constructed(self):
        channel_id = self.id_generator.generate_viable_id()
        exception = BotChannelHasScrimException(channel_id)
        self.assertEqual(f"Cannot create a scrim on channel <#{channel_id}> because the channel already has an active "
                         f"scrim.", exception.message)
