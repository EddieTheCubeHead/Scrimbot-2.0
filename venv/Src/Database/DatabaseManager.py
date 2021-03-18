import sqlite3
import os

class DatabaseManager():
    def __init__(self, db_folder = "DBFiles"):
        # If the bot is run first time  the database needs to be initialized
        do_init = not (os.path.isdir(f"./{db_folder}") and os.path.isfile(f"./{db_folder}/games.db")
                                and os.path.isfile(f"./{db_folder}/servers.db"))

        if not os.path.isdir(f"./{db_folder}"):
            try:
                os.mkdir(f"./{db_folder}")
            except OSError:
                full_path = os.getcwd()
                print(f"Error creating database folder at {full_path}/{db_folder}; shutting down.")

        self.game_connection = sqlite3.connect(f"{db_folder}/games.db")
        self.server_connection = sqlite3.connect(f"{db_folder}/servers.db")

        if do_init:
            self.initialize_tables()

    def initialize_tables(self):



# Enable initializing the database without starting the bot by making this file executable and run the initialization
# script on execute
if __name__ == "__main__":
    init_manager = DatabaseManager()