__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import AsyncMock, MagicMock

from discord import Member

from Bot.Checks.PermissionsCheck import PermissionsCheck
from Bot.DataClasses.GuildMember import PermissionLevel
from Bot.Exceptions.BotInvalidPermissionsException import BotInvalidPermissionsException
from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestPermissionsCheck(AsyncUnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()

    def setUp(self) -> None:
        self.context = MagicMock()
        self.user: Member = MagicMock()
        self.user.guild_permissions.administrator = False
        self.context.author = self.user
        self.context.command.name = "test"

    async def test_check_given_requires_admin_permissions_when_admin_permissions_present_then_check_succeeds(self):
        check = PermissionsCheck(PermissionLevel.admin)
        self._set_discord_admin()
        self.assertTrue(await check.check(self.context))

    async def test_check_given_requires_admin_permission_when_admin_permission_not_present_then_check_fails(self):
        check = PermissionsCheck(PermissionLevel.admin)
        expected_exception = BotInvalidPermissionsException(self.context, PermissionLevel.admin, PermissionLevel.member)
        await self._async_assert_raises_correct_exception(expected_exception, check.check, self.context)

    def _set_discord_admin(self):
        self.user.guild_permissions.administrator = True


