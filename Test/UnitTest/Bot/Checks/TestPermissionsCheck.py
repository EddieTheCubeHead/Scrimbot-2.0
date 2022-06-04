__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import AsyncMock

from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestPermissionsCheck(AsyncUnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()

    def setUp(self) -> None:
        self.context = AsyncMock()

    def test_check_given_requires_bot_admin_permissions_when_admin_permissions_present_then_check_succeeds(self):
        pass
