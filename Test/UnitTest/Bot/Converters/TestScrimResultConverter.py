__version__ = "0.1"
__author__ = "Eetu Asikainen"

import unittest
from unittest.mock import MagicMock

from Bot.Converters.ScrimResultConverter import ScrimResultConverter
from Bot.DataClasses.Scrim import Scrim
from Bot.DataClasses.Team import Team
from Bot.DataClasses.UserScrimResult import Result
from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestScrimResultConverter(AsyncUnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_mocker = TestIdGenerator()

    def setUp(self) -> None:
        self.mock_connection = MagicMock()
        self.converter = ScrimResultConverter(self.mock_connection)
        self.mock_context = MagicMock()
        self.mock_scrim = MagicMock()
        self.mock_context.scrim = self.mock_scrim
        self.mock_teams_manager = MagicMock()
        self.mock_scrim.teams_manager = self.mock_teams_manager

    async def test_convert_given_numerical_argument_from_scrim_teams_then_corresponding_result_returned_and_saved(self):
        teams = self._setup_teams("Team 1", "Team 2")
        result = await self.converter.convert(self.mock_context, "2")
        self.assertEqual([(teams[1],), (teams[0],)], result)
        added_scrim = self.mock_connection.add_scrim.call_args[0][0]
        self.assertEqual("Team 2", added_scrim.teams[0].team.name)
        self.assertEqual("Team 1", added_scrim.teams[1].team.name)
        self.assertEqual(1, added_scrim.teams[0].placement)
        self.assertEqual(2, added_scrim.teams[1].placement)

    async def test_convert_given_text_argument_from_scrim_teams_then_corresponding_result_returned_and_saved(self):
        teams = self._setup_teams("Team 1", "Team 2")
        result = await self.converter.convert(self.mock_context, "Team 2")
        self.assertEqual([(teams[1],), (teams[0],)], result)
        added_scrim = self.mock_connection.add_scrim.call_args[0][0]
        self.assertEqual("Team 2", added_scrim.teams[0].team.name)
        self.assertEqual("Team 1", added_scrim.teams[1].team.name)
        self.assertEqual(1, added_scrim.teams[0].placement)
        self.assertEqual(2, added_scrim.teams[1].placement)

    def _setup_teams(self, *names: str) -> list[Team]:
        mocked_teams = []
        for name in names:
            mock_team = MagicMock()
            mock_team.name = name
            mocked_teams.append(mock_team)
        self.mock_teams_manager.get_game_teams.return_value = mocked_teams
        return mocked_teams
