__version__ = "ver"
__author__ = "Eetu Asikainen"

from asyncio import gather, sleep, create_task
from unittest.mock import MagicMock

from Bot.Converters.ScrimConverter import ScrimConverter
from Bot.DataClasses.Scrim import Scrim
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
