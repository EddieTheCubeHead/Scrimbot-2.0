__version__ = "0.1"
__author__ = "Eetu Asikainen"

import sqlite3
import os
import sys
import json

from discord.ext import commands

class DatabaseManager():
    """A class to serve as an abstraction layer between the bot and the database."""

    def __init__(self, db_folder = "DBFiles"):

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
        cursor = self._game_connection.cursor()

        with open(f"{self._path}/SQLScripts/CreateGamesTable.sql") as create_games_table:
            cursor.execute(create_games_table.read())

        with open(f"{self._path}/SQLScripts/CreateAliasesTable.sql") as create_aliases_table:
            cursor.execute(create_aliases_table.read())

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
        cursor = self._server_connection.cursor()

        with open(f"{self._path}/SQLScripts/CreateScrimsTable.sql") as create_scrims_table:
            cursor.execute(create_scrims_table.read())

        self.__server_connection.commit()
        cursor.close()

    def fetch_scrim(self, channel_id: int):
        cursor = self._server_connection.cursor()
        cursor.execute("SELECT * FROM Scrims WHERE ChannelID = ?", (channel_id,))
        scrim_row = cursor.fetchone()
        cursor.close()

        return scrim_row

    def register_scrim_channel(self, channel_id: int, team_1_voice_id: int = None, team_2_voice_id: int = None,
                               spectator_voice_id: int = None):

        if self.fetch_scrim(channel_id):
            raise commands.UserInputError(message="This channel is already registered for scrim usage.")

        cursor = self._server_connection.cursor()

        cursor.execute("INSERT INTO Scrims (ChannelID, Team1VoiceID, Team2VoiceID, SpectatorVoiceID) \
                        VALUES (?, ?, ?, ?)", (channel_id, team_1_voice_id, team_2_voice_id, spectator_voice_id))

        self._server_connection.commit()
        cursor.close()

    def update_scrim_channel(self, channel_id: int, team_1_voice_id: int = None, team_2_voice_id: int = None,
                               spectator_voice_id: int = None):

        if not self.fetch_scrim(channel_id):
            raise commands.UserInputError(message="This channel is not registered for scrim usage.")

        cursor = self._server_connection.cursor()

        cursor.execute("UPDATE Scrims SET (Team1VoiceID = ?, Team2VoiceID = ?, SpectatorVoiceID = ?) \
                                WHERE ChannelID = ?",
                       (team_1_voice_id, team_2_voice_id, spectator_voice_id, channel_id))

        self._server_connection.commit()
        cursor.close()

    def remove_scrim_channel(self, channel_id: int):

        if not self.fetch_scrim(channel_id):
            raise commands.UserInputError(message="This channel is not registered for scrim usage.")

        cursor = self._server_connection.cursor()

        cursor.execute("DELETE FROM Scrims WHERE ChannelID = ?", channel_id)

    def check_voice_availability(self, channel_id: int):

        cursor = self._server_connection.cursor()

        cursor.execute("SELECT * FROM Scrims WHERE (Team1VoiceID = ? OR Team2VoiceID = ? OR SpectatorVoiceID = ?)",
                       (channel_id, channel_id, channel_id))

        return cursor.fetchone()

    def games_init_generator(self):

        game_cursor = self._game_connection.cursor()

        game_cursor.execute("SELECT * FROM Games")

        for game in game_cursor:
            alias_cursor = self._game_connection.cursor()

            alias_cursor.execute("SELECT Alias FROM GameAliases WHERE GameName = ?", (game[0],))
            aliases = [alias[0] for alias in alias_cursor.fetchall()]

            yield(game[0], game[1], game[2], game[3], game[4], aliases)



# Enable initializing the database without starting the bot by making this file executable and running the
# initialization logic on execute
if __name__ == "__main__":
    init_manager = DatabaseManager()