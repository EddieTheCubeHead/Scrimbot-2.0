__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Bot.Exceptions.BotUnregisteredChannelException import BotUnregisteredChannelException
from Utils.TestBases.UnittestBase import UnittestBase
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestBotUnregisteredChannelException(UnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()

    def test_init_given_channel_id_then_message_with_channel_mention_constructed(self):
        channel_id = self.id_generator.generate_viable_id()
        exception = BotUnregisteredChannelException(channel_id)
        self.assertEqual(f"Cannot create a scrim on channel <#{channel_id}> because it is not registered for scrim "
                         f"usage.", exception.message)
