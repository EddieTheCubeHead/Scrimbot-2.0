__version__ = "0.1"
__author__ = "Eetu Asikainen"

import datetime
from time import sleep
from unittest.mock import MagicMock

from Src.Bot.Cogs.Helpers.WaitingScrimService import WaitingScrimService
from Src.Bot.DataClasses.User import User
from Utils.TestBases.UnittestBase import UnittestBase
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator
from Utils.TestHelpers.test_utils import assert_almost_now


def _get_over_five_minutes_ago() -> datetime.datetime:
    return datetime.datetime.now() - datetime.timedelta(minutes=5, milliseconds=1)


class TestWaitingScrimService(UnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()

    def setUp(self) -> None:
        self.waiting_scrim_service = WaitingScrimService()

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_dependency(WaitingScrimService)

    def test_register_scrim_when_called_with_unregistered_scrim_then_scrim_added_to_listeners(self):
        mock_scrim = MagicMock()
        self.waiting_scrim_service.register(mock_scrim)
        assert_almost_now(self.waiting_scrim_service.waiting_scrims[mock_scrim])

    def test_register_scrim_when_called_with_registered_scrim_then_timestamp_not_updated(self):
        mock_scrim = MagicMock()
        self.waiting_scrim_service.register(mock_scrim)
        assert_almost_now(self.waiting_scrim_service.waiting_scrims[mock_scrim])
        original_timestamp = self.waiting_scrim_service.waiting_scrims[mock_scrim]
        sleep(0.001)
        self.waiting_scrim_service.register(mock_scrim)
        self.assertEqual(original_timestamp, self.waiting_scrim_service.waiting_scrims[mock_scrim])

    def test_get_scrim_when_called_with_member_of_waiting_scrim_then_the_correct_scrim_returned(self):
        mock_scrim = MagicMock()
        another_mock_scrim = MagicMock()
        mock_member = MagicMock()
        mock_member.id = self.id_generator.generate_viable_id()
        mock_scrim.teams_manager.all_participants = [User(mock_member.id)]
        self.waiting_scrim_service.waiting_scrims[mock_scrim] = datetime.datetime.now()
        self.waiting_scrim_service.waiting_scrims[another_mock_scrim] = datetime.datetime.now()
        self.assertEqual(mock_scrim, self.waiting_scrim_service.get_scrim(mock_member))

    def test_get_scrim_when_called_with_member_of_no_waiting_scrim_then_no_scrim_returned(self):
        mock_scrim = MagicMock()
        mock_member = MagicMock()
        self.waiting_scrim_service.waiting_scrims[mock_scrim] = datetime.datetime.now()
        self.assertIsNone(self.waiting_scrim_service.get_scrim(mock_member))

    def test_prune_observers_given_no_observers_over_five_minutes_old_then_nothing_happens(self):
        mock_scrim = MagicMock()
        self.waiting_scrim_service.waiting_scrims[mock_scrim] = datetime.datetime.now()
        self.waiting_scrim_service.prune()
        self.assertIn(mock_scrim, self.waiting_scrim_service.waiting_scrims)

    def test_prune_observers_given_observer_over_five_minutes_old_then_observer_removed_and_returned(self):
        mock_scrim = MagicMock()
        self.waiting_scrim_service.waiting_scrims[mock_scrim] = _get_over_five_minutes_ago()
        pruned = self.waiting_scrim_service.prune()
        self.assertNotIn(mock_scrim, self.waiting_scrim_service.waiting_scrims)
        self.assertIn(mock_scrim, pruned)
        mock_scrim.cancel_voice_wait.assert_called()

    def test_prune_observers_given_old_and_young_observers_then_only_old_observers_removed(self):
        mock_old_scrim = MagicMock()
        self.waiting_scrim_service.waiting_scrims[mock_old_scrim] = _get_over_five_minutes_ago()
        mock_young_scrim = MagicMock()
        self.waiting_scrim_service.waiting_scrims[mock_young_scrim] = datetime.datetime.now()
        pruned = self.waiting_scrim_service.prune()
        self.assertNotIn(mock_old_scrim, self.waiting_scrim_service.waiting_scrims)
        self.assertIn(mock_young_scrim, self.waiting_scrim_service.waiting_scrims)
        self.assertIn(mock_old_scrim, pruned)

    def test_prune_observers_given_multiple_old_observers_then_only_old_observers_removed(self):
        for _ in range(5):
            self.waiting_scrim_service.waiting_scrims[MagicMock()] = _get_over_five_minutes_ago()
        pruned = self.waiting_scrim_service.prune()
        self.assertEqual(0, len(self.waiting_scrim_service.waiting_scrims))
        self.assertEqual(5, len(pruned))

    def test_unregister_when_called_then_scrim_removed_from_listeners(self):
        mock_scrim = MagicMock()
        self.waiting_scrim_service.waiting_scrims[mock_scrim] = datetime.datetime.now()
        self.waiting_scrim_service.unregister(mock_scrim)
        self.assertNotIn(mock_scrim, self.waiting_scrim_service.waiting_scrims)

    def test_unregister_when_called_with_not_registered_scrim_then_no_exception_thrown(self):
        self.waiting_scrim_service.unregister(MagicMock())
