__version__ = "ver"
__author__ = "Eetu Asikainen"

from unittest.mock import AsyncMock, MagicMock

from Bot.Converters.ScsrimManagerConverter import ScrimManagerConverter
from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestScrimManagerConverter(AsyncUnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()

    def setUp(self) -> None:
        self.scrim_converter = MagicMock()
        self.converter = ScrimManagerConverter(self.scrim_converter)

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_dependency(ScrimManagerConverter)

    async def test_wrap_scrim_when_used_as_context_manager_then_scrim_fetched_from_converter_and_yielded(self):
        mock_scrim = MagicMock()
        self.scrim_converter.fetch_scrim.return_value.__aenter__.return_value = mock_scrim
        async with self.converter.wrap_scrim(self.id_generator.generate_viable_id()) as scrim:
            self.assertEqual(mock_scrim, scrim)
