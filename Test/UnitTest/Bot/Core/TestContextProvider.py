__version__ = "ver"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock, AsyncMock

from Bot.Core.ScrimContext import ScrimContext
from Utils.AsyncUnittestBase import AsyncUnittestBase
from Bot.Core.ContextProvider import ContextProvider


class TestContextProvider(AsyncUnittestBase):

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_dependency(ContextProvider)

    async def test_get_context_given_client_and_message_then_super_get_context_called_with_custom_context_class(self):
        mock_super = AsyncMock()
        mock_message = MagicMock()
        provider = ContextProvider()
        await provider.get_context(mock_super, mock_message)
        mock_super.get_context.assert_called_with(mock_message, cls=ScrimContext)
