__version__ = "0.1"
__author__ = "Eetu Asikainen"

import sqlite3
import os
import sys
import json
from typing import Optional, List, Tuple

from discord.ext import commands

from Src.Bot.DataClasses.Game import Game


class DatabaseManager:
    """A class to serve as an abstraction layer between the bot and the database.

    methods
    -------

    fetch_scrim(channel_id)
        Fetch the scrim info of the given channel from the database

    register_scrim_channel(channel_id, team_1_voice_id, team_2_voice_id, spectator_voice_id)
        Register a new channel for scrim usage into the database

    update_scrim_channel(channel_id, team_1_voice_id, team_2_voice_id, spectator_voice_id)
        Update channel data in the database

    remove_scrim_channel(channel_id)
        Remove a scrim channel from the database

    check_voice_availability(channel_id)
        Check whether the given channel is already reserved for voice usage in other scrims

    games_init_generator()
        A generator that can be used to initialize the games supported by the bot from the games in the database
    """

    def __init__(self, db_folder="DBFiles"):
        """The constructor of DatabaseManager

        args
        ----

        :param db_folder: The folder in which the database files are storen, default "DBFiles"
        :type db_folder: str
        """

        self._path = os.path.join(os.path.dirname(__file__))

        # If the bot is run the first time the database needs to be initialized
        init_databases = not (os.path.isdir(f"{self._path}/{db_folder}")
                              and os.path.isfile(f"{self._path}/{db_folder}/games.db")
                              and os.path.isfile(f"{self._path}/{db_folder}/servers.db"))

        if not os.path.isdir(f"{self._path}/{db_folder}"):
            print("Didn't find a database file folder. Creating a new one.")
            try:
                os.mkdir(f"{self._path}/{db_folder}")
            except OSError:
                print(f"Error creating database folder at {self._path}/{db_folder}; shutting down.")
                sys.exit(1)

        self._game_connection = sqlite3.connect(f"{self._path}/{db_folder}/games.db")
        self._server_connection = sqlite3.connect(f"{self._path}/{db_folder}/servers.db")

        if init_databases:
            # Games are stored in a database instead of just using the init json to enable possible user-added custom
            # games later on
            print("Didn't find established database files. Initializing the databases")
            self._init_games()
            self._init_servers()

    def _init_games(self):
        """A private helper method that creates the games-database based on scripts in the SQLScripts folder"""

        cursor = self._game_connection.cursor()

        for subject in ("Games", "Aliases", "Matches", "Participants", "Elo"):
            with open(f"{self._path}/SQLScripts/Create{subject}Table.sql") as create_table_script:
                cursor.execute(create_table_script.read())

        with open(f"{self._path}/games_init.json") as games:
            games_dict = json.load(games)

        for category in games_dict:
            for game in games_dict[category]:
                cursor.execute("INSERT INTO Games (Name, Colour, Icon, Playercount, Type) VALUES (?, ?, ?, ?, ?)",
                               (game, games_dict[category][game]['colour'], games_dict[category][game]['icon'],
                                games_dict[category][game]['playercount'], category))

                for alias in games_dict[category][game]['alias']:
                    cursor.execute("INSERT INTO GameAliases (GameName, Alias) VALUES (?, ?)",
                                   (game, alias))

        self._game_connection.commit()
        cursor.close()

    def _init_servers(self):
        """A private helper method that creates the servers-table based on the scripts in the SQLScripts folder"""

        cursor = self._server_connection.cursor()

        with open(f"{self._path}/SQLScripts/CreateScrimsTable.sql") as create_scrims_table:
            cursor.execute(create_scrims_table.read())

        with open(f"{self._path}/SQLScripts/CreateServersTable.sql") as create_servers_table:
            cursor.execute(create_servers_table.read())

        with open(f"{self._path}/SQLScripts/CreateServerAdministratorsTable.sql") as create_server_admins_table:
            cursor.execute(create_server_admins_table.read())

        self._server_connection.commit()
        cursor.close()

    def fetch_scrim(self, channel_id: int) -> Optional[sqlite3.Row]:
        """A method for fetching a row containing the data of a specified scrim from the database

        args
        ----

        :param channel_id: The unique discord id of the channel of which to fetch scrim data of
        :type channel_id: int
        :return: An sqlite row-object of the data
        :rtype: Optional[sqlite3.Row]
        """

        cursor = self._server_connection.cursor()
        cursor.execute("SELECT * FROM Scrims WHERE ChannelID = ?", (channel_id,))
        scrim_row = cursor.fetchone()
        cursor.close()

        return scrim_row

    def register_scrim_channel(self, channel_id: int, team_1_voice_id: int = None, team_2_voice_id: int = None,
                               spectator_voice_id: int = None):
        """A method for registering a new channel for scrim usage

        args
        ----

        :param channel_id: The channel id of the channel to regiser
        :type channel_id: int
        :param team_1_voice_id: The channel id of the optional voice channel for team 1
        :type team_1_voice_id: Optional[int]
        :param team_2_voice_id: The channel id of the optional voice channel for team 2
        :type team_2_voice_id: Optional[int]
        :param spectator_voice_id: The channel id of the optional spectator voice channel
        :type spectator_voice_id: Optional[int]
        """

        if self.fetch_scrim(channel_id):
            raise commands.UserInputError(message="This channel is already registered for scrim usage.")

        cursor = self._server_connection.cursor()

        cursor.execute("INSERT INTO Scrims (ChannelID, Team1VoiceID, Team2VoiceID, SpectatorVoiceID) \
                        VALUES (?, ?, ?, ?)", (channel_id, team_1_voice_id, team_2_voice_id, spectator_voice_id))

        self._server_connection.commit()
        cursor.close()

    def update_scrim_channel(self, channel_id: int, team_1_voice_id: int = None, team_2_voice_id: int = None,
                             spectator_voice_id: int = None):
        """A method for updating channel data for scrim channels

        args
        ----

        :param channel_id: The channel id of the channel to update data of
        :type channel_id: int
        :param team_1_voice_id: The new channel id of the optional voice channel for team 1
        :type team_1_voice_id: Optional[int]
        :param team_2_voice_id: The new channel id of the optional voice channel for team 2
        :type team_2_voice_id: Optional[int]
        :param spectator_voice_id: The new channel id of the optional spectator voice channel
        :type spectator_voice_id: Optional[int]
        """

        if not self.fetch_scrim(channel_id):
            raise commands.UserInputError(message="This channel is not registered for scrim usage.")

        cursor = self._server_connection.cursor()

        cursor.execute("UPDATE Scrims SET Team1VoiceID = ?, Team2VoiceID = ?, SpectatorVoiceID = ? WHERE ChannelID = ?",
                       (team_1_voice_id, team_2_voice_id, spectator_voice_id, channel_id))

        self._server_connection.commit()
        cursor.close()

    def remove_scrim_channel(self, channel_id: int):
        """A method for removing all channel data of the given channel

        args
        ----

        :param channel_id: The channel id of the channel of which data should be deleted
        :type channel_id: int
        """

        if not self.fetch_scrim(channel_id):
            raise commands.UserInputError(message="This channel is not registered for scrim usage.")

        cursor = self._server_connection.cursor()

        cursor.execute("DELETE FROM Scrims WHERE ChannelID = ?", [channel_id])

    def check_voice_availability(self, channel_id: int) -> Optional[sqlite3.Row]:
        """A method to ensure the given channel id is not reserved for voice usage for other scrims

        :param channel_id: The channel id of the channel to check availability of
        :type channel_id: int
        :return: A row object containing data of the reserved scrim if reserved, otherwise None
        :rtype: Optional[sqlite3.Row]
        """

        cursor = self._server_connection.cursor()

        cursor.execute("SELECT * FROM Scrims WHERE (Team1VoiceID = ? OR Team2VoiceID = ? OR SpectatorVoiceID = ?)",
                       (channel_id, channel_id, channel_id))

        return cursor.fetchone()

    def games_init_generator(self) -> Tuple[str, str, str, str, int, Optional[List[str]]]:
        """A generator that yields the data of all games stored in the database, one game per iteration.

        :return: A tuple containing all the data required in the Game constructor
        :rtype: tuple[str, str, str, str, int, Optional[list[str]]]
        """

        game_cursor = self._game_connection.cursor()

        game_cursor.execute("SELECT * FROM Games")

        for game in game_cursor:
            alias_cursor = self._game_connection.cursor()

            alias_cursor.execute("SELECT Alias FROM GameAliases WHERE GameName = ?", (game[0],))
            aliases = [alias[0] for alias in alias_cursor.fetchall()]

            yield *game, aliases

    def set_player_elo(self, player_id: int, elo: int, game: Game):
        """A method that updates a player's elo in the table or creates a new record if the player has no elo

        :param player_id: The discord id ("snowflake") of the player whose elo should be updated
        :type player_id: int
        :param elo: The new elo value of the player
        :type elo: int
        :param game: The game
        :type game:
        """


# Enable initializing the database without starting the bot by making this file executable and running the
# initialization logic on execution
if __name__ == "__main__":
    init_manager = DatabaseManager()
