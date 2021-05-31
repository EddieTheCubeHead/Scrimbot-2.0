__version__ = "0.1"
__author__ = "Eetu Asikainen"

import unittest
import os
import shutil
import sqlite3
from typing import Tuple, Optional, List

import test_utils
from Src.Database.ServersDatabaseManager import ServersDatabaseManager
from Src.Database.DatabaseConnectionWrapper import DatabaseConnectionWrapper


def _setup_disposable_folder_manager(disposable_folder_name: str, disposable_file_name: str) -> \
        ServersDatabaseManager:
    if not disposable_folder_name:
        raise Exception("Passing null string into setup disposable folder manager!")
    disposable_folder_manager = ServersDatabaseManager(disposable_folder_name, disposable_file_name)
    if os.path.exists(disposable_folder_manager.db_folder_path):
        shutil.rmtree(disposable_folder_manager.db_folder_path)

    return disposable_folder_manager


def _parse_voice_channel_rows(raw_rows) -> List[Optional[int]]:
    parsed_rows = []
    if raw_rows[0][1] == 0:
        parsed_rows.append(None)
        raw_rows.pop(0)
    for row in raw_rows:
        parsed_rows.append(row[0])
    return parsed_rows


class TestServersDatabaseManager(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.manager: ServersDatabaseManager = ServersDatabaseManager.from_raw_file_path(":memory:")
        cls.manager.setup_manager()
        cls.id_mocker = test_utils.UniqueIdGenerator()

    def test_given_uninitialized_folder_then_folder_created(self):
        disposable_folder = "DisposableServersTest"
        disposable_manager = _setup_disposable_folder_manager(disposable_folder, "unused.db")
        disposable_manager.ensure_correct_folder_structure()
        self.assertIn(disposable_folder, os.listdir(disposable_manager.path))
        shutil.rmtree(disposable_manager.db_folder_path)

    def test_given_normal_setup_then_all_tables_initialized(self):
        for table in ("ScrimTextChannels", "ScrimVoiceChannels", "Servers", "ServerAdministrators"):
            self._assert_table_exists(table)

    def test_given_valid_id_then_scrim_found(self):
        expected_text, expected_voices = self._generate_scrim_data(2)
        self._register_test_channel(expected_text, *expected_voices)
        actual_text, actual_voices = self.manager.fetch_scrim(expected_text)
        self._assert_equal_scrim_channels(actual_text, actual_voices, expected_text, expected_voices)

    def test_given_valid_scrim_data_then_scrim_inserted_successfully(self):
        expected_text, expected_voices = self._generate_scrim_data(4)
        self.manager.register_scrim_channel(expected_text, *expected_voices)
        actual_text, actual_voices = self._fetch_from_registered(expected_text)
        self._assert_equal_scrim_channels(actual_text, actual_voices, expected_text, expected_voices)

    def test_given_text_channel_deleted_then_cascades_to_all_voice_channels(self):
        deleted_text, deleted_voices = self._generate_scrim_data(3)
        self._register_test_channel(deleted_text, *deleted_voices)
        self.manager.remove_scrim_channel(deleted_text)
        self._assert_channels_removed([pair[0] for pair in deleted_voices])

    def test_given_scrim_channels_in_db_when_channel_data_updated_then_correct_values_found(self):
        original_text, original_voices = self._generate_scrim_data(6)
        self._register_test_channel(original_text, * original_voices)
        updated_voices = self._generate_voice_channel_data(6)
        self.manager.update_scrim_voice_channels(original_text, updated_voices)
        actual_text, actual_voices = self._fetch_from_registered(original_text)
        self._assert_equal_scrim_channels(original_text, updated_voices, actual_text, actual_voices)

    def test_given_voice_channel_in_db_then_channel_availability_returns_data(self):
        text_id, voice_data = self._generate_scrim_data(1)
        self._register_test_channel(text_id, *voice_data)
        self.assertIsNotNone(self.manager.check_voice_availability(voice_data[0][0]))

    def test_given_voice_channel_not_in_db_then_channel_availability_returns_none(self):
        free_voice_id = self.id_mocker.generate_nonviable_id()
        self.assertIsNone(self.manager.check_voice_availability(free_voice_id))

    def _assert_table_exists(self, table: str):
        with DatabaseConnectionWrapper(self.manager.connection) as cursor:
            cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name=?;", (table,))
            self.assertEqual(cursor.fetchone()[0], 1, f"Expected to find table '{table}'")

    def _assert_equal_scrim_channels(self, actual_text, actual_voices, expected_text, expected_voices):
        self.assertEqual(expected_text, actual_text)
        self.assertListEqual(expected_voices, actual_voices)

    def _register_test_channel(self, text_channel_id: int, *voice_channel_data: Tuple[int, int]):
        self._insert_scrim_text_channel(text_channel_id)
        for team_voice_id, team_number in voice_channel_data:
            self._insert_scrim_voice_channel(team_voice_id, team_number, text_channel_id)

    def _insert_scrim_text_channel(self, text_channel_id):
        with DatabaseConnectionWrapper(self.manager.connection) as cursor:
            cursor.execute("INSERT INTO ScrimTextChannels (ChannelID) VALUES (?)", (text_channel_id,))

    def _insert_scrim_voice_channel(self, lobby_voice_id, channel_team, text_channel_id):
        with DatabaseConnectionWrapper(self.manager.connection) as cursor:
            cursor.execute("INSERT INTO ScrimVoiceChannels (ChannelID, ChannelTeam, ParentTextChannel)"
                           "VALUES (?, ?, ?)", (lobby_voice_id, channel_team, text_channel_id))

    def _fetch_from_registered(self, channel_id) -> Tuple[int, List[Tuple[int, int]]]:
        text_channel_id = self._fetch_scrim_text_channel(channel_id)
        voice_channel_data = self._fetch_scrim_voice_channels(channel_id)

        return text_channel_id[0], voice_channel_data

    def _fetch_scrim_text_channel(self, channel_id) -> sqlite3.Row:
        with DatabaseConnectionWrapper(self.manager.connection) as cursor:
            cursor.execute("SELECT * FROM ScrimTextChannels WHERE ChannelID=?", (channel_id,))
            result = cursor.fetchone()
        return result

    def _fetch_scrim_voice_channels(self, parent_text_id) -> List[Tuple[int, int]]:
        with DatabaseConnectionWrapper(self.manager.connection) as cursor:
            cursor.execute("SELECT * FROM ScrimVoiceChannels WHERE ParentTextChannel=? ORDER BY ChannelTeam",
                           (parent_text_id,))
            raw_rows = cursor.fetchall()
        return [(row[0], row[1]) for row in raw_rows]

    def _generate_scrim_data(self, voice_channel_count: int = 1, *, include_lobby_channel=True) \
            -> Tuple[int, List[Tuple[int, int]]]:
        lobby_offset = 0 if include_lobby_channel else 1
        mock_text_channel = self.id_mocker.generate_viable_id()
        channel_group_size = voice_channel_count + 1 - lobby_offset
        inverted_channel_team_pairs = self._generate_voice_channel_data(channel_group_size, lobby_offset=lobby_offset)
        return mock_text_channel, inverted_channel_team_pairs

    def _generate_voice_channel_data(self, channel_group_size, *, lobby_offset=0):
        mock_team_channels: List[int] = self.id_mocker.generate_viable_id_group(channel_group_size)
        inverted_channel_team_pairs = [(v, k) for k, v in enumerate(mock_team_channels, lobby_offset)]
        return inverted_channel_team_pairs

    def _assert_channels_removed(self, channels: List[int]):
        for channel in channels:
            with DatabaseConnectionWrapper(self.manager.connection) as cursor:
                cursor.execute("SELECT * FROM ScrimVoiceChannels WHERE ChannelID=?", (channel,))
                self.assertIsNone(cursor.fetchone())


if __name__ == '__main__':
    unittest.main()
