__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Test.Utils.TestHelpers.id_parser import try_get_id
from Test.Utils.TestHelpers.test_utils import create_mock_guild, create_mock_author


class UserFetchPatcher:

    def __init__(self, context):
        self._context = context

    def __call__(self, user_id: int):
        guild_id = try_get_id(self._context, "guild_id")
        guild = create_mock_guild(guild_id)
        return create_mock_author(user_id, guild, self._context)
