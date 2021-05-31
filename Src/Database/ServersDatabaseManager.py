__version__ = "0.1"
__author__ = "Eetu Asikainen"

import sqlite3
import os
import sys
import json
from typing import Optional, List, Tuple, Dict, Union
from abc import ABC, abstractmethod

from discord.ext import commands

from Bot.DataClasses.Game import Game
from Src.Database.DatabaseManager import DatabaseManager
from Src.Database.DatabaseConnectionWrapper import DatabaseConnectionWrapper
from Bot.Exceptions.BotBaseUserException import BotBaseUserException
from Bot.Exceptions.BotBaseInternalException import BotBaseInternalException


class ServersDatabaseManager(DatabaseManager):

    def __init__(self, db_folder: str = "DBFiles", db_file: str = "servers.db"):
        super().__init__(db_folder, db_file)

    @classmethod
    def from_raw_file_path(cls, db_file_path: str):
        new_manager = cls("", "")
        new_manager.db_file_path = db_file_path
        return new_manager

    def init_database(self):
        super()._create_tables("ScrimTextChannels", "ScrimVoiceChannels", "Servers", "ServerAdministrators")

    def fetch_scrim(self, channel_id: int) -> Tuple[int, List[Tuple[int, int]]]:
        """A method for fetching a row containing the data of a specified scrim from the database

        args
        ----

        :param channel_id: The unique discord id of the channel of which to fetch scrim data of
        :type channel_id: int
        :return: An sqlite row-object of the data
        :rtype: Optional[sqlite3.Row]
        """

        scrim_text_channel = self._fetch_scrim_text_channel(channel_id)
        scrim_voice_channels = self._fetch_scrim_voice_channels(channel_id)
        if not scrim_text_channel:
            raise BotBaseInternalException(f"Tried to fetch a scrim with text channel id of {channel_id}, "
                                           f"but found nothing.")

        return scrim_text_channel[0], scrim_voice_channels

    def register_scrim_channel(self, text_channel: int, *voice_channel_data: Tuple[int, int]):
        """A method for registering a new channel for scrim usage

        args
        ----

        :param text_channel: The channel id of the channel to register
        :type text_channel: int
        :param voice_channel_data: The data of registered voice channels. First int is channel id, second team number
        Team number of 0 indicates lobby channels used for organizing scrims and for hosting spectators during play.
        :type voice_channel_data: List[Tuple[int, int]]
        """

        if self._fetch_scrim_text_channel(text_channel):
            raise BotBaseUserException(message="This channel is already registered for scrim usage.")

        self._insert_scrim_text_channel(text_channel)
        for voice_channel_id, voice_channel_team in voice_channel_data:
            self._insert_scrim_voice_channel(voice_channel_id, voice_channel_team, text_channel)

    def remove_scrim_channel(self, channel_id: int):
        """A method for removing all channel data of the given channel

        args
        ----

        :param channel_id: The channel id of the channel of which data should be deleted
        :type channel_id: int
        """

        if not self._fetch_scrim_text_channel(channel_id):
            raise commands.UserInputError(message="This channel is not registered for scrim usage.")

        with DatabaseConnectionWrapper(self.connection) as cursor:
            cursor.execute("DELETE FROM ScrimTextChannels WHERE ChannelID = ?", (channel_id,))

    def update_scrim_voice_channels(self, channel_id: int, voice_channel_data: List[Tuple[int, int]]):
        """A method for updating channel data for scrim channels

        args
        ----

        :param channel_id: The channel id of the channel to update data of
        :type channel_id: int
        :param voice_channel_data: The data of registered voice channels. First int is channel id, second team number
        Team number of 0 indicates lobby channels used for organizing scrims and for hosting spectators during play.
        :type voice_channel_data: List[Tuple[int, int]]
        """

        if not self._fetch_scrim_text_channel(channel_id):
            raise commands.UserInputError(message="This channel is not registered for scrim usage.")

        self._delete_voice_channel_data(channel_id)
        for voice_channel_id, voice_channel_team in voice_channel_data:
            self._insert_scrim_voice_channel(voice_channel_id, voice_channel_team, channel_id)

    def check_voice_availability(self, channel_id: int) -> Optional[sqlite3.Row]:
        """A method to ensure the given channel id is not reserved for voice usage for other scrims

        :param channel_id: The channel id of the channel to check availability of
        :type channel_id: int
        :return: A row object containing data of the reserved scrim if reserved, otherwise None
        :rtype: Optional[sqlite3.Row]
        """

        with DatabaseConnectionWrapper(self.connection) as cursor:
            cursor.execute("SELECT * FROM ScrimVoiceChannels WHERE ChannelID=?", (channel_id,))
            registered_row = cursor.fetchone()

        return registered_row

    def _insert_scrim_text_channel(self, channel_id):
        with DatabaseConnectionWrapper(self.connection) as cursor:
            cursor.execute("INSERT INTO ScrimTextChannels (ChannelID) \
                            VALUES (?)", (channel_id,))

    def _insert_scrim_voice_channel(self, voice_channel_id: int, voice_channel_team: int, parent_channel_id: int):
        with DatabaseConnectionWrapper(self.connection) as cursor:
            cursor.execute("INSERT INTO ScrimVoiceChannels (ChannelID, ChannelTeam, ParentTextChannel)"
                           "VALUES (?, ?, ?)", (voice_channel_id, voice_channel_team, parent_channel_id))

    def _fetch_scrim_text_channel(self, channel_id) -> Optional:
        with DatabaseConnectionWrapper(self.connection) as cursor:
            cursor.execute("SELECT * FROM ScrimTextChannels WHERE ChannelID = ?", (channel_id,))
            scrim_text_channel = cursor.fetchone()
        return scrim_text_channel

    def _fetch_scrim_voice_channels(self, parent_channel_id: int):
        with DatabaseConnectionWrapper(self.connection) as cursor:
            cursor.execute("SELECT * FROM ScrimVoiceChannels WHERE ParentTextChannel=?"
                           "ORDER BY ChannelTeam", (parent_channel_id,))
            raw_rows = cursor.fetchall()
        return [(row[0], row[1]) for row in raw_rows]

    def _delete_voice_channel_data(self, channel_id):
        with DatabaseConnectionWrapper(self.connection) as cursor:
            cursor.execute("DELETE FROM ScrimVoiceChannels WHERE ParentTextChannel=?", (channel_id,))
