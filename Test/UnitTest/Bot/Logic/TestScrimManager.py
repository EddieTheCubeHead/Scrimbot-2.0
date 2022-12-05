__version__ = "0.1"
__author__ = "Eetu Asikainen"

import unittest
from unittest import skip
from unittest.mock import MagicMock, AsyncMock

from Bot.DataClasses.Team import Team
from Bot.Exceptions.BotInvalidStateChangeException import BotInvalidStateChangeException
from Bot.Exceptions.BuildException import BuildException
from Test.Utils.TestHelpers.TestIdGenerator import TestIdGenerator
from Bot.Logic.ScrimTeamsManager import ScrimTeamsManager
from Bot.Logic.ScrimManager import ScrimManager
from Bot.Exceptions.BotBaseRespondToContextException import BotBaseRespondToContextException
from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase


@unittest.skip("Waiting for scrim state rewrite")
class TestScrimManager(AsyncUnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_mocker = TestIdGenerator()

    def setUp(self) -> None:
        self.mock_teams_manager = MagicMock()
        self.mock_teams_manager.try_move_to_voice = AsyncMock()
        self.scrim_manager = ScrimManager(self.mock_teams_manager)

    def test_hash_when_called_uses_message_id(self):
        mock_message = MagicMock()
        mock_message.id = self.id_mocker.generate_viable_id()
        self.scrim_manager.message = mock_message
        self.assertEqual(mock_message.id, hash(self.scrim_manager))

    def test_hash_when_called_with_no_message_then_build_exception_raised(self):
        expected_exception = BuildException("Tried to hash a scrim manager with no message")
        self._assert_raises_correct_exception(expected_exception, hash, self.scrim_manager)

    def test_add_participant_given_valid_participant_then_add_called_in_teams_manager(self):
        participant = MagicMock()
        participant.id = self.id_mocker.generate_viable_id()
        self.scrim_manager.add_participant(participant)
        self.mock_teams_manager.add_player.assert_called_with(ScrimTeamsManager.PARTICIPANTS, participant)

    def test_lock_given_enough_participants_then_locked_correctly(self):
        self.mock_teams_manager.has_enough_participants = True
        self.scrim_manager.lock()
        self.assertEqual(LOCKED, self.scrim_manager.state)
        self.mock_teams_manager.clear_queue.assert_called_with()

    def test_lock_given_too_few_participants_then_error_raised(self):
        self.mock_teams_manager.has_enough_participants = False
        expected_exception = BotBaseRespondToContextException("Could not lock the scrim. Too few participants present.",
                                                              delete_after=60)
        self._assert_raises_correct_exception(expected_exception, self.scrim_manager.lock)
        self.mock_teams_manager.clear_queue.assert_not_called()

    def test_lock_given_scrim_not_in_lfp_state_then_error_raised(self):
        self.mock_teams_manager.has_enough_participants = True
        invalid_states = (LOCKED, CAPS, CAPS_PREP, VOICE_WAIT, STARTED)
        for state in invalid_states:
            with self.subTest(f"Locking with invalid state: {state.description}", delete_after=60):
                self.scrim_manager.state = state
                expected_exception = BotInvalidStateChangeException(state, LOCKED)
                self._assert_raises_correct_exception(expected_exception, self.scrim_manager.lock)
                self.mock_teams_manager.clear_queue.assert_not_called()

    def test_start_given_valid_teams_and_state_then_state_changed(self):
        self.mock_teams_manager.has_participants = False
        self.mock_teams_manager.has_full_teams = True
        valid_states = (LOCKED, CAPS)
        for state in valid_states:
            with self.subTest(f"Starting with valid state: {state.description}"):
                self.scrim_manager.state = state
                self.scrim_manager.start()
                self.assertEqual(STARTED, self.scrim_manager.state)

    def test_start_given_participants_left_and_valid_state_then_error_raised(self):
        mock_ctx = MagicMock()
        self.mock_teams_manager.has_participants = True
        self.mock_teams_manager.has_full_teams = True
        self.scrim_manager.state = LOCKED
        expected_exception = BotBaseRespondToContextException("Could not start the scrim. All participants are not in "
                                                              "a team.", send_help=False)
        actual_exception = self._assert_raises_correct_exception(expected_exception, self.scrim_manager.start)
        self.assertEqual(expected_exception.get_help_portion(mock_ctx), actual_exception.get_help_portion(mock_ctx))

    def test_start_given_participants_empty_but_not_all_min_sizes_met_and_valid_state_then_error_raised(self):
        mock_ctx = MagicMock()
        self.mock_teams_manager.has_participants = False
        self.mock_teams_manager.has_full_teams = False
        self.scrim_manager.state = LOCKED
        expected_exception = BotBaseRespondToContextException("Could not start the scrim. Some teams lack the minimum "
                                                              "number of players required.", send_help=False)
        actual_exception = self._assert_raises_correct_exception(expected_exception, self.scrim_manager.start)
        self.assertEqual(expected_exception.get_help_portion(mock_ctx), actual_exception.get_help_portion(mock_ctx))

    def test_start_given_participants_left_and_not_all_min_sizes_met_and_valid_state_then_correct_error_raised(self):
        mock_ctx = MagicMock()
        self.mock_teams_manager.has_participants = True
        self.mock_teams_manager.has_full_teams = False
        self.scrim_manager.state = LOCKED
        expected_exception = BotBaseRespondToContextException("Could not start the scrim. Some teams lack the minimum "
                                                              "number of players required.", send_help=False)
        actual_exception = self._assert_raises_correct_exception(expected_exception, self.scrim_manager.start)
        self.assertEqual(expected_exception.get_help_portion(mock_ctx), actual_exception.get_help_portion(mock_ctx))

    async def test_start_with_voice_given_valid_conditions_then_move_voice_called_from_teams_manager(self):
        self.mock_teams_manager.has_participants = False
        self.mock_teams_manager.has_full_teams = True
        self.mock_teams_manager.all_players_in_voice_chat = True
        self.mock_teams_manager.try_move_to_voice.return_value = True
        valid_states = (LOCKED, CAPS)
        for state in valid_states:
            with self.subTest(f"Starting with voice chat when in valid state: {state.description}"):
                self.scrim_manager.state = state
                self.assertTrue(await self.scrim_manager.start_with_voice())
                self.mock_teams_manager.try_move_to_voice.assert_called()

    async def test_start_with_voice_given_move_fails_then_false_returned(self):
        self.mock_teams_manager.has_participants = False
        self.mock_teams_manager.has_full_teams = True
        self.mock_teams_manager.all_players_in_voice_chat = True
        self.mock_teams_manager.try_move_to_voice.return_value = False
        valid_states = (LOCKED, CAPS)
        for state in valid_states:
            with self.subTest(f"Starting with voice chat when in valid state: {state.description}"):
                self.scrim_manager.state = state
                self.assertFalse(await self.scrim_manager.start_with_voice())
                self.mock_teams_manager.try_move_to_voice.assert_called()

    async def test_start_with_voice_given_invalid_state_then_error_raised(self):
        self.mock_teams_manager.has_participants = False
        self.mock_teams_manager.has_full_teams = True
        self.mock_teams_manager.all_players_in_voice_chat = True
        invalid_states = (LFP, STARTED, CAPS_PREP)
        for state in invalid_states:
            with self.subTest(f"Starting with voice chat when in invalid state: {state.description}"):
                self.scrim_manager.state = state
                expected_exception = BotInvalidStateChangeException(state, VOICE_WAIT)
                await self._async_assert_raises_correct_exception(expected_exception,
                                                                  self.scrim_manager.start_with_voice)

    async def test_start_with_voice_given_participants_left_then_error_raised(self):
        mock_ctx = MagicMock()
        self.mock_teams_manager.has_participants = True
        self.mock_teams_manager.has_full_teams = True
        self.mock_teams_manager.all_players_in_voice_chat = True
        self.scrim_manager.state = LOCKED
        expected_exception = BotBaseRespondToContextException("Could not start the scrim. All participants are not in "
                                                              "a team.", send_help=False)
        actual_exception = await self._async_assert_raises_correct_exception(expected_exception,
                                                                             self.scrim_manager.start_with_voice)
        self.assertEqual(expected_exception.get_help_portion(mock_ctx), actual_exception.get_help_portion(mock_ctx))

    def test_cancel_voice_wait_when_called_then_state_changed_to_locked(self):
        self.scrim_manager.state = VOICE_WAIT
        self.scrim_manager.cancel_voice_wait()
        self.assertEqual(LOCKED, self.scrim_manager.state)

    async def test_end_given_two_teams_when_called_with_winner_then_scrim_ended_with_winner_data(self):
        self.scrim_manager.state = STARTED
        self.mock_teams_manager.move_to_lobby = AsyncMock()
        result = [(MagicMock(),), (MagicMock(),)]
        await self.scrim_manager.end(result)
        self.assertEqual(ENDED, self.scrim_manager.state)
        self.assertEqual(result, self.mock_teams_manager.result)
        self.mock_teams_manager.move_to_lobby.assert_called()

    def test_terminate_when_called_with_author_then_state_set_to_terminated_and_terminator_set_to_teams_manager(self):
        states = (LFP, LOCKED, CAPS_PREP, CAPS, VOICE_WAIT, STARTED)
        mock_author = MagicMock()
        mock_author.id = self.id_mocker.generate_viable_id()
        for state in states:
            with self.subTest(f"Terminating scrim in state {state}"):
                self.scrim_manager.state = state
                self.scrim_manager.terminate(mock_author)
                self.assertEqual(TERMINATED, self.scrim_manager.state)
                self.assertEqual(mock_author.id, self.mock_teams_manager.terminator)

    def test_terminate_when_called_with_ended_scrim_then_invalid_state_change_raised(self):
        mock_author = MagicMock()
        mock_author.id = self.id_mocker.generate_viable_id()
        self.mock_teams_manager.terminator = None
        self.scrim_manager.state = ENDED
        expected_exception = BotInvalidStateChangeException(ENDED, TERMINATED)
        self._assert_raises_correct_exception(expected_exception, self.scrim_manager.terminate, mock_author)
        self.assertIsNone(self.mock_teams_manager.terminator)

    def test_build_description_calls_state_build_with_teams_manager(self):
        mock_state = MagicMock()
        mock_state.build_description.return_value = "Correct"
        self.scrim_manager.state = mock_state
        self.assertEqual("Correct", self.scrim_manager.build_description())
        mock_state.build_description.assert_called_with(self.mock_teams_manager)

    def test_build_fields_calls_state_build_with_teams_manager(self):
        mock_state = MagicMock()
        mock_state.build_fields.return_value = [("Correct", "Fields", False)]
        self.scrim_manager.state = mock_state
        self.assertEqual([("Correct", "Fields", False)], self.scrim_manager.build_fields())
        mock_state.build_fields.assert_called_with(self.mock_teams_manager)

    def test_build_footer_calls_state_build_with_teams_manager(self):
        mock_state = MagicMock()
        mock_state.build_footer.return_value = "Correct"
        self.scrim_manager.state = mock_state
        self.assertEqual("Correct", self.scrim_manager.build_footer())
        mock_state.build_footer.assert_called_with(self.mock_teams_manager)
