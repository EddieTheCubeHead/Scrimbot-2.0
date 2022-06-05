__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Bot.Core.ScrimContext import ScrimContext
from Bot.DataClasses.GuildMember import PermissionLevel
from Bot.Exceptions.BotInvalidPermissionsException import BotInvalidPermissionsException
from Utils.TestBases.UnittestBase import UnittestBase
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestBotInvalidPermissionsException(UnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_mocker = TestIdGenerator()

    def setUp(self) -> None:
        self.context: ScrimContext = MagicMock()
        self.context.command.name = 'test'

    def test_init_given_permissions_levels_given_then_message_constructed(self):
        self._assert_correct_message(PermissionLevel.admin, PermissionLevel.member)

    def _assert_correct_message(self, required_permissions: PermissionLevel, actual_permissions: PermissionLevel):
        expected_message = f"Using command 'test' requires at least {required_permissions} level rights for this " \
                           f"guild. (Your permission level: {actual_permissions})"
        actual_error = BotInvalidPermissionsException(self.context, required_permissions, actual_permissions)
        self.assertEqual(expected_message, actual_error.message)

