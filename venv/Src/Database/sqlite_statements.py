import sqlite3
import json

def init_games(connection: sqlite3.Connection):
    cursor = connection.cursor()

    with open("SQLScripts/CreateGamesTable.sql") as create_games_table:
        cursor.execute(create_games_table.read())

    with open("SQLScripts/CreateAliasesTable.sql") as create_aliases_table:
        cursor.execute(create_aliases_table.read())

    with open("games_init.json") as games:
        games_dict = json.load(games)

    for category in games_dict:
        for game in games_dict[category]:
            cursor.execute("INSERT INTO Games (Name, Dispname, Colour, Icon, Playercount, Type) \
                                VALUES (?, ?, ?, ?, ?, ?);",
                            (game, games_dict[category][game]['dispname'], games_dict[category][game]['colour'],
                            games_dict[category][game]['icon'], games_dict[category][game]['playercount'], category))

            for alias in games_dict[category][game]['alias']:
                cursor.execute("INSERT INTO GameAliases (GameName, Alias) VALUES (?, ?)",
                                (game, alias))

    connection.commit()
    cursor.close()

    print_table(connection, "Games")
    print_table(connection, "GameAliases")

def print_table(connection: sqlite3.Connection, tablename: str):
    cursor = connection.cursor()

    cursor.execute(f"SELECT * FROM {tablename};")

    for row in cursor:
        print(row)