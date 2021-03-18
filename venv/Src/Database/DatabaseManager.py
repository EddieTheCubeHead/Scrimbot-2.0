import sqlite3
import os
import sys
import json
import Src.Database.sqlite_statements as sqlite_statements

class DatabaseManager():
    def __init__(self, db_folder = "DBFiles"):

        # If the bot is run the first time the database needs to be initialized
        do_init = not (os.path.isdir(f"./{db_folder}") and os.path.isfile(f"./{db_folder}/games.db")
                                and os.path.isfile(f"./{db_folder}/servers.db"))

        if not os.path.isdir(f"./{db_folder}"):
            print("Didn't find a database file folder. Creating a new one.")
            try:
                os.mkdir(f"./{db_folder}")
            except OSError:
                full_path = os.getcwd()
                print(f"Error creating database folder at {full_path}/{db_folder}; shutting down.")
                sys.exit(1)

        self.game_connection = sqlite3.connect(f"{db_folder}/games.db")
        self.server_connection = sqlite3.connect(f"{db_folder}/servers.db")

        if do_init:
            # Games are stored in a database instead of just using the init json to enable possible user-added custom
            # games later on
            print("Didn't find established database files. Initializing the databases")
            sqlite_statements.init_games(self.game_connection)





# Enable initializing the database without starting the bot by making this file executable and running the
# initialization script on execute
if __name__ == "__main__":
    init_manager = DatabaseManager()