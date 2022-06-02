__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from behave.runner import Context

from Bot.Core.ScrimContext import ScrimContext


class MockMemberConverter:

    @staticmethod
    async def convert(ctx: ScrimContext, arg: str):
        mock_member = MagicMock()
        mock_member.id = int(arg)
        return mock_member

    def __call__(self, *args, **kwargs):
        return self
