__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock
from unittest import IsolatedAsyncioTestCase

from Utils.UnittestBase import UnittestBase
from Utils.TestIdGenerator import TestIdGenerator
from Bot.Logic.ScrimTeamsManager import ScrimTeamsManager
from Bot.Logic.Scrim import Scrim
from Bot.DataClasses.ScrimState import ScrimState
from Bot.Exceptions.BotBaseUserException import BotBaseUserException
from Bot.Exceptions.BotBaseInternalException import BotBaseInternalException


class TestScrim(UnittestBase, IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_mocker = TestIdGenerator()

    def setUp(self) -> None:
        self.mock_manager = MagicMock()
        self.scrim = Scrim(self.mock_manager)

    def test_add_participant_given_valid_participant_then_add_called_in_teams_manager(self):
        participant = MagicMock()
        participant.id = self.id_mocker.generate_viable_id()
        self.scrim.add_participant(participant)
        self.mock_manager.add_player.assert_called_with(ScrimTeamsManager.PARTICIPANTS, participant)

    def test_lock_given_enough_participants_then_locked_correctly(self):
        self.mock_manager.has_enough_participants = True
        self.scrim.lock()
        self.assertEqual(ScrimState.LOCKED, self.scrim.state)
        self.mock_manager.clear_queue.assert_called_with()

    def test_lock_given_too_few_participants_then_error_raised(self):
        self.mock_manager.has_enough_participants = False
        expected_exception = BotBaseUserException("Could not lock the scrim. Too few participants present.")
        self._assert_raises_correct_exception(expected_exception, self.scrim.lock)
        self.mock_manager.clear_queue.assert_not_called()

    def test_lock_given_scrim_not_in_lfp_state_then_silent_error_raised(self):
        self.mock_manager.has_enough_participants = True
        invalid_states = (ScrimState.LOCKED, ScrimState.CAPS, ScrimState.CAPS_PREP, ScrimState.VOICE_WAIT,
                          ScrimState.STARTED)
        for state in invalid_states:
            with self.subTest(f"Locking with invalid state: {state.name}"):
                self.scrim.state = state
                expected_exception = BotBaseInternalException("Tried to perform an invalid state change from state "
                                                              f"{state.name} to {ScrimState.LOCKED.name}")
                self._assert_raises_correct_exception(expected_exception, self.scrim.lock)
                self.mock_manager.clear_queue.assert_not_called()

    def test_start_given_valid_teams_and_state_then_state_changed(self):
        self.mock_manager.has_participants = False
        self.mock_manager.has_full_teams = True
        valid_states = (ScrimState.LOCKED, ScrimState.CAPS)
        for state in valid_states:
            with self.subTest(f"Starting with valid state: {state.name}"):
                self.scrim.state = state
                self.scrim.start()
                self.assertEqual(ScrimState.STARTED, self.scrim.state)

    def test_start_given_participants_left_and_valid_state_then_error_raised(self):
        mock_ctx = MagicMock()
        self.mock_manager.has_participants = True
        self.mock_manager.has_full_teams = True
        self.scrim.state = ScrimState.LOCKED
        expected_exception = BotBaseUserException("Could not start the scrim. All participants are not in a team.",
                                                  send_help=False)
        actual_exception = self._assert_raises_correct_exception(expected_exception, self.scrim.start)
        self.assertEqual(expected_exception.get_help_portion(mock_ctx), actual_exception.get_help_portion(mock_ctx))

    def test_start_given_participants_empty_but_not_all_min_sizes_met_and_valid_state_then_error_raised(self):
        mock_ctx = MagicMock()
        self.mock_manager.has_participants = False
        self.mock_manager.has_full_teams = False
        self.scrim.state = ScrimState.LOCKED
        expected_exception = BotBaseUserException("Could not start the scrim. Some teams lack the minimum number of "
                                                  "players required.", send_help=False)
        actual_exception = self._assert_raises_correct_exception(expected_exception, self.scrim.start)
        self.assertEqual(expected_exception.get_help_portion(mock_ctx), actual_exception.get_help_portion(mock_ctx))

    def test_start_given_participants_left_and_not_all_min_sizes_met_and_valid_state_then_correct_error_raised(self):
        mock_ctx = MagicMock()
        self.mock_manager.has_participants = True
        self.mock_manager.has_full_teams = False
        self.scrim.state = ScrimState.LOCKED
        expected_exception = BotBaseUserException("Could not start the scrim. Some teams lack the minimum number of "
                                                  "players required.", send_help=False)
        actual_exception = self._assert_raises_correct_exception(expected_exception, self.scrim.start)
        self.assertEqual(expected_exception.get_help_portion(mock_ctx), actual_exception.get_help_portion(mock_ctx))

    def test_start_with_voice_given_valid_conditions_then_move_voice_called_from_teams_manager(self):
        self.mock_manager.has_participants = False
        self.mock_manager.has_full_teams = True
        self.mock_manager.all_players_in_voice_chat = True
        valid_states = (ScrimState.LOCKED, ScrimState.CAPS)
        for state in valid_states:
            with self.subTest(f"Starting with voice chat when in valid state: {state.name}"):
                self.scrim.state = state
                self.scrim.start_with_voice()
                self.mock_manager.try_move_to_voice.assert_called()

    def test_start_with_voice_given_invalid_state_then_error_raised(self):
        self.mock_manager.has_participants = False
        self.mock_manager.has_full_teams = True
        self.mock_manager.all_players_in_voice_chat = True
        invalid_states = (ScrimState.LFP, ScrimState.STARTED, ScrimState.VOICE_WAIT, ScrimState.CAPS_PREP)
        for state in invalid_states:
            with self.subTest(f"Starting with voice chat when in invalid state: {state.name}"):
                self.scrim.state = state
                expected_exception = BotBaseInternalException("Tried to perform an invalid state change from state "
                                                              f"{state.name} to {ScrimState.VOICE_WAIT.name}")
                self._assert_raises_correct_exception(expected_exception, self.scrim.start_with_voice)

    def test_start_with_voice_given_participants_left_then_error_raised(self):
        mock_ctx = MagicMock()
        self.mock_manager.has_participants = True
        self.mock_manager.has_full_teams = True
        self.mock_manager.all_players_in_voice_chat = True
        self.scrim.state = ScrimState.LOCKED
        expected_exception = BotBaseUserException("Could not start the scrim. All participants are not in a team.",
                                                  send_help=False)
        actual_exception = self._assert_raises_correct_exception(expected_exception, self.scrim.start_with_voice)
        self.assertEqual(expected_exception.get_help_portion(mock_ctx), actual_exception.get_help_portion(mock_ctx))
