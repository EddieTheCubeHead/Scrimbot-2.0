__version__ = "ver"
__author__ = "Eetu Asikainen"

from asyncio import gather, sleep, create_task
from unittest.mock import MagicMock

from Src.Bot.Converters.ScrimConverter import ScrimConverter
from Src.Bot.DataClasses.ParticipantTeam import ParticipantTeam
from Src.Bot.DataClasses.Scrim import Scrim
from Src.Bot.DataClasses.Team import PARTICIPANTS, SPECTATORS, QUEUE
from Src.Bot.Exceptions.BotChannelHasScrimException import BotChannelHasScrimException
from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator
from Utils.TestHelpers.async_waiter import WaitChecker, Waiter


def _create_mock_teams(*team_names: str) -> [ParticipantTeam]:
    teams = []
    for team_name in team_names:
        mock_participant_team = MagicMock()
        mock_team = MagicMock()
        mock_team.members = []
        mock_team.name = team_name
        mock_participant_team.team = mock_team
        teams.append(mock_participant_team)
    return teams


class TestScrimConverter(AsyncUnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()

    def setUp(self) -> None:
        self.connection = MagicMock()
        self.converter = ScrimConverter(self.connection)

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_dependency(ScrimConverter)

    async def test_fetch_scrim_when_called_with_valid_id_then_scrim_provided_to_context_manager(self):
        mock_scrim = self._create_mock_scrim()
        self.connection.get_active_scrim.return_value = mock_scrim
        async with self.converter.fetch_scrim(mock_scrim.channel_id) as actual_scrim:
            self.assertEqual(mock_scrim, actual_scrim)

    async def test_fetch_scrim_when_exited_then_scrim_saved(self):
        mock_scrim = self._create_mock_scrim()
        self.connection.get_active_scrim.return_value = mock_scrim
        async with self.converter.fetch_scrim(mock_scrim.channel_id):
            pass
        self.connection.edit_scrim.assert_called()

    async def test_fetch_scrim_when_same_scrim_fetch_attempted_twice_then_second_waits_for_first_context(self):
        wait_checker = WaitChecker()
        first_event = Waiter(wait_checker, "1")
        second_event = Waiter(wait_checker, "2")
        mock_scrim = self._create_mock_scrim()
        self.connection.get_active_scrim.return_value = mock_scrim
        first_task = create_task(self._start_fetch_task(first_event, mock_scrim.channel_id))
        second_task = create_task(self._start_fetch_task(second_event, mock_scrim.channel_id))
        await sleep(0)
        second_event.finish()
        first_event.finish()
        await gather(second_task, first_task)
        self.assertEqual(first_event, wait_checker.first)

    async def test_fetch_scrim_when_different_scrim_fetch_attempted_then_both_fetches_concurrent(self):
        wait_checker = WaitChecker()
        first_event = Waiter(wait_checker, "1")
        second_event = Waiter(wait_checker, "2")
        mock_scrim_1 = self._create_mock_scrim()
        mock_scrim_2 = self._create_mock_scrim()
        self.connection.get_active_scrim.side_effect \
            = lambda x: mock_scrim_1 if x == mock_scrim_1.channel_id else mock_scrim_2
        first_task = create_task(self._start_fetch_task(first_event, mock_scrim_1.channel_id))
        second_task = create_task(self._start_fetch_task(second_event, mock_scrim_2.channel_id))
        await sleep(0)
        second_event.finish()
        first_event.finish()
        await gather(second_task, first_task)
        self.assertEqual(second_event, wait_checker.first)

    async def test_create_scrim_when_no_scrim_on_channel_then_returns_new_scrim_from_channel_and_game(self):
        mock_game = self._create_mock_game()
        mock_channel = self._create_mock_channel()
        expected_scrim = Scrim(mock_channel, mock_game)
        self._shallow_assert_equal_scrim(expected_scrim, await self.converter.create_scrim(mock_channel, mock_game))

    async def test_create_scrim_when_scrim_created_then_scrim_saved_to_database(self):
        mock_game = self._create_mock_game()
        mock_channel = self._create_mock_channel()
        actual_scrim = await self.converter.create_scrim(mock_channel, mock_game)
        self.connection.add_scrim.assert_called_with(actual_scrim)

    async def test_create_scrim_when_scrim_created_then_setup_teams_created_and_saved_to_database(self):
        mock_game = self._create_mock_game()
        mock_channel = self._create_mock_channel()
        actual_scrim = await self.converter.create_scrim(mock_channel, mock_game)

        self.assertEqual(5, len(actual_scrim.teams))
        for team, size in ((PARTICIPANTS, 10), (SPECTATORS, 0), (QUEUE, 0), ("Team 1", 5), ("Team 2", 5)):
            self._assert_team_created(team, size, actual_scrim)

    def test_exists_when_called_with_existing_scrim_then_returns_true(self):
        mock_scrim = self._create_mock_scrim()
        self.connection.exists.return_value = True
        self.assertTrue(self.converter.exists(mock_scrim.channel_id))

    def test_exists_when_called_with_invalid_scrim_then_returns_false(self):
        self.connection.exists.return_value = False
        self.assertFalse(self.converter.exists(self.id_generator.generate_nonviable_id()))

    async def _start_fetch_task(self, waiter: Waiter, channel_id: int):
        async with self.converter.fetch_scrim(channel_id):
            await waiter.start()

    def _create_mock_scrim(self) -> Scrim:
        scrim = MagicMock()
        scrim.channel_id = self.id_generator.generate_viable_id()
        return scrim

    def _create_mock_game(self, name: str = None):
        if name is None:
            name = str(self.id_generator.generate_viable_id())
        mock_game = MagicMock()
        mock_game.name = name
        mock_game.max_team_size = 5
        mock_game.team_count = 2
        return mock_game

    def _create_mock_channel(self, channel_id: int = None):
        if channel_id is None:
            channel_id = self.id_generator.generate_viable_id()
        mock_channel = MagicMock()
        mock_channel.channel_id = channel_id
        return mock_channel

    def _shallow_assert_equal_scrim(self, expected_scrim: Scrim, actual_scrim: Scrim):
        self.assertEqual(expected_scrim.game_name, actual_scrim.game_name)
        self.assertEqual(expected_scrim.scrim_id, actual_scrim.scrim_id)
        self.assertEqual(expected_scrim.channel_id, actual_scrim.channel_id)

    def _assert_team_created(self, team_name: str, team_size: int, scrim: Scrim):
        team = next(participant_team for participant_team in scrim.teams if participant_team.team.name == team_name)
        self.assertIsNotNone(team)
        self.assertEqual(team_size, team.max_size)
