__version__ = "ver"
__author__ = "Eetu Asikainen"

import unittest
from unittest.mock import MagicMock

from Src.Bot.Converters.ScrimManagerConverter import ScrimManagerConverter
from Utils.TestBases.UnittestBase import UnittestBase
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestScrimManagerConverter(UnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()

    def setUp(self) -> None:
        self.scrim_converter = MagicMock()
        self.converter = ScrimManagerConverter(self.scrim_converter)

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_dependency(ScrimManagerConverter)

    @unittest.skip(reason="Waiting for redo of ScrimManager and TeamsManager builders")
    def test_wrap_scrim_when_given_a_scrim_then_wraps_scrim_in_teams_manager_and_manager(self):
        mock_scrim = MagicMock()
        actual_scrim = self.converter.wrap_scrim(mock_scrim)
        self.assertEqual()
