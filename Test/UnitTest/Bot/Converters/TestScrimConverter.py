__version__ = "ver"
__author__ = "Eetu Asikainen"

from asyncio import gather, sleep, create_task
from unittest.mock import MagicMock

from Bot.Converters.ScrimConverter import ScrimConverter
from Bot.DataClasses.Scrim import Scrim
from Bot.Exceptions.BotChannelHasScrimException import BotChannelHasScrimException
from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator
from Utils.TestHelpers.async_waiter import WaitChecker, Waiter


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
        actual_scrim = self.converter.create_scrim(mock_channel, mock_game)
        self.connection.add_scrim.assert_called_with(actual_scrim)

    async def test_create_scrim_when_scrim_on_channel_then_exception_raised(self):
        mock_game = self._create_mock_game()
        mock_channel = self._create_mock_channel()
        expected_exception = BotChannelHasScrimException(mock_channel.channel_id)
        await self.converter.create_scrim(mock_channel, mock_game)
        self._assert_raises_correct_exception(expected_exception, self.converter.create_scrim, mock_channel, mock_game)

    async def test_create_scrim_when_scrim_created_then_channel_lock_acquired(self):
        mock_game = self._create_mock_game()
        mock_channel = self._create_mock_channel()
        await self.converter.create_scrim(mock_channel, mock_game)
        self.assertTrue(self.converter._scrims[mock_channel.channel_id].locked(()))

    def test_exists_when_called_with_existing_scrim_then_returns_true(self):
        mock_scrim = self._create_mock_scrim()
        self.connection.exists.return_value = True
        self.assertTrue(self.converter.exists(mock_scrim.channel_id))

    def test_exists_when_called_with_invalid_scrim_then_returns_false(self):
        self.connection.exists.return_value = False
        self.assertFalse(self.converter.exists(self.id_generator.generate_nonviable_id()))

    async def test_set_message_when_called_with_scrim_and_message_then_message_added_to_scrim_and_scrim_saved(self):
        pass

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
