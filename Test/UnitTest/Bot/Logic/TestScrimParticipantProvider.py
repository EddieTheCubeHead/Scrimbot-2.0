__version__ = "0.1"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Bot.Exceptions.BotAlreadyParticipantException import BotAlreadyParticipantException
from Bot.Exceptions.BotInvalidJoinException import BotInvalidJoinException
from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase
from Bot.Logic.ScrimParticipantProvider import ScrimParticipantProvider
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestScrimParticipantProvider(AsyncUnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()

    def setUp(self) -> None:
        self.mock_client = MagicMock()
        self.manager = ScrimParticipantProvider()
        self.manager.client = self.mock_client
        self.mock_reaction = MagicMock()

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_dependency(ScrimParticipantProvider)

    def test_try_add_participant_given_id_not_in_dict_then_participant_added(self):
        mock_member = MagicMock()
        mock_id = self.id_generator.generate_viable_id()
        mock_member.id = mock_id
        self.manager.try_add_participant(mock_member)
        self.assertIn(mock_id, self.manager.participants)

    def test_try_add_participant_given_id_in_dict_then_error_raised(self):
        mock_member = MagicMock()
        mock_id, mock_guild_id = self.id_generator.generate_viable_id_group(2)
        mock_member.id = mock_id
        self.manager.participants[mock_id] = mock_guild_id
        expected_exception = BotAlreadyParticipantException(mock_member)
        self._assert_raises_correct_exception(expected_exception, self.manager.try_add_participant, mock_member)

    def test_try_get_participant_given_id_in_dict_then_member_returned(self):
        mock_member = MagicMock()
        mock_id, mock_guild_id = self.id_generator.generate_viable_id_group(2)
        self.manager.participants[mock_id] = mock_guild_id
        mock_guild = MagicMock()
        self.mock_client.get_guild.return_value = mock_guild
        mock_guild.get_member.return_value = mock_member
        self.assertEqual(mock_member, self.manager.try_get_participant(mock_id))

    def test_assert_not_participant_given_id_in_dict_then_error_raised(self):
        mock_member = MagicMock()
        mock_id, mock_guild_id = self.id_generator.generate_viable_id_group(2)
        mock_member.id = mock_id
        self.manager.participants[mock_id] = mock_guild_id
        expected_exception = BotAlreadyParticipantException(mock_member)
        self._assert_raises_correct_exception(expected_exception, self.manager.ensure_not_participant, mock_member)

    def test_assert_not_participant_given_id_not_in_dict_then_no_error_raised(self):
        mock_member = MagicMock()
        mock_id = self.id_generator.generate_viable_id()
        mock_member.id = mock_id
        self.manager.ensure_not_participant(mock_member)

    def test_drop_participants_when_called_with_participants_then_all_given_participants_dropped(self):
        mock_participant_ids = self.id_generator.generate_viable_id_group(10)
        mock_guild_id = self.id_generator.generate_viable_id()
        for participant_id in mock_participant_ids:
            self.manager.participants[participant_id] = mock_guild_id
        self.manager.drop_participants(*mock_participant_ids)
        self.assertEqual(0, len(self.manager.participants))

