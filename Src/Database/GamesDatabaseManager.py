__version__ = "0.1"
__author__ = "Eetu Asikainen"

import json
from typing import List, Tuple, Dict, Union, Any

from Bot.Exceptions.BotLoggedContextException import BotLoggedContextException
from Database.DatabaseManager import DatabaseManager
from Database.DatabaseConnectionWrapper import DatabaseConnectionWrapper
from Database.Exceptions.DatabaseMissingRowException import DatabaseMissingRowException
from Database.Exceptions.DatabaseDuplicateUniqueRowException import DatabaseDuplicateUniqueRowException
from Database.Exceptions.DatabasePrimaryKeyViolatedException import DatabasePrimaryKeyViolatedException
from Database.Exceptions.DatabaseForeignKeyViolatedException import DatabaseForeignKeyViolatedException


class GamesDatabaseManager(DatabaseManager):

    def __init__(self, db_folder: str = "DataFiles", db_file: str = "games.db"):
        super().__init__(db_folder, db_file)

    @classmethod
    def from_raw_file_path(cls, db_file_path: str):
        new_manager = cls("", "")
        new_manager.db_file_path = db_file_path
        return new_manager

    def init_database(self):
        self._create_tables("Games", "Aliases", "Matches", "Participants", "UserElos")

        with open(f"{self.path}/../Configs/games.json", encoding="utf-8") as games_file:
            games: Dict[str, Dict[str, Union[str, int]]] = json.load(games_file)

        for game_item in games.items():
            game_data, aliases = _get_game_data_from_dict_item(game_item)
            self.register_new_game(game_data, aliases)

    def games_init_generator(self) -> Tuple[str, str, str, int, int, int, List[str]]:
        """A generator that yields the data of all games stored in the database, one game per iteration.

        :return: A tuple containing all the data required in the Game constructor
        :rtype: tuple[str, str, str, str, int, Optional[list[str]]]
        """

        with DatabaseConnectionWrapper(self) as cursor:

            cursor.execute("SELECT * FROM Games")
            game_rows = cursor.fetchall()

            for game in game_rows:
                aliases = self._fetch_aliases(game)

                yield *game, aliases

    def insert_user_elo(self, player_id: int, game: str, elo: int = 1700):
        """A method that inserts a new player elo into the UserElos table

        :param player_id: The discord id ("snowflake") of the player whose elo should be updated
        :type player_id: int
        :param elo: The new elo value of the player
        :type elo: int
        :param game: The game
        :type game: str
        """
        self._assert_unique_elo(player_id, game)
        if not self._game_exists(game):
            raise DatabaseForeignKeyViolatedException("UserElos", "Game", game, "Games", "Name")
        _validate_inserted_elo(elo)
        self._insert_player_elo(elo, game, player_id)

    def _assert_unique_elo(self, player_id: int, game: str):
        if self._user_elo_exists(player_id, game):
            raise DatabasePrimaryKeyViolatedException("UserElos", ["Snowflake", "Game"], [str(player_id), game])

    def _user_elo_exists(self, player_id, game):
        with DatabaseConnectionWrapper(self) as cursor:
            cursor.execute("SELECT Count(*) FROM UserElos WHERE Snowflake=? AND Game=?", (player_id, game))
            existing_count = cursor.fetchone()[0]
        return existing_count > 0

    def _insert_player_elo(self, elo, game, player_id):
        with DatabaseConnectionWrapper(self) as cursor:
            cursor.execute("INSERT INTO UserElos (Snowflake, Elo, Game) VALUES (?, ?, ?)", (player_id, elo, game))

    def _fetch_aliases(self, game):
        with DatabaseConnectionWrapper(self) as cursor:
            cursor.execute("SELECT Alias FROM Aliases WHERE GameName = ?", (game[0],))
            aliases = [alias[0] for alias in cursor.fetchall()]
        return aliases

    def register_new_game(self, game_data: Tuple[str, str, str, int, int, int], aliases: List[str] = None):
        if self._game_exists(game_data[0]):
            raise DatabaseDuplicateUniqueRowException("Games", "Name", game_data[0])
        if aliases:
            self._validate_aliases(aliases)
        self._insert_game_with_aliases(game_data, aliases)

    def _validate_aliases(self, aliases):
        for alias in aliases:
            self._validate_alias(alias)

    def _game_exists(self, game_name):
        with DatabaseConnectionWrapper(self) as cursor:
            cursor.execute("SELECT Count(*) FROM Games WHERE Name=?", (game_name,))
            return cursor.fetchone()[0] != 0

    def _insert_game_with_aliases(self, game_data, aliases):
        self._insert_game(game_data)
        if aliases:
            self._insert_aliases(game_data[0], aliases)

    def _insert_game(self, game_data):
        with DatabaseConnectionWrapper(self) as cursor:
            cursor.execute("INSERT INTO Games (Name, Colour, Icon, MinTeamSize, MaxTeamSize, TeamCount)"
                           "VALUES (?, ?, ?, ?, ?, ?)", game_data)

    def _insert_aliases(self, game_name, aliases):
        with DatabaseConnectionWrapper(self) as cursor:
            for alias in aliases:
                cursor.execute("INSERT INTO Aliases (GameName, Alias) VALUES (?, ?)",
                               (game_name, alias))

    def add_match(self, game_name: str, winner: int, participants: List[Tuple[int, int, int]]) -> int:
        match_id = self._insert_match(game_name, winner)
        self._insert_participants(game_name, match_id, participants)
        return match_id

    def _insert_match(self, game_name: str, winner: int):
        with DatabaseConnectionWrapper(self) as cursor:
            cursor.execute("INSERT INTO Matches (Game, Winner) VALUES (?, ?)",
                           (game_name, winner))
            return cursor.lastrowid

    def _insert_participants(self, game_name: str, match_id: int, participants: List[Tuple[int, int, int]]):
        for player in participants:
            self._insert_participant(game_name, match_id, player)

    def _insert_participant(self, game_name: str, match_id: int, participant: Tuple[int, int, int]):
        with DatabaseConnectionWrapper(self) as cursor:
            cursor.execute("INSERT INTO Participants (MatchID, Game, ParticipantID, Team, FrozenElo) "
                           "VALUES (?, ?, ?, ?, ?)", (match_id, game_name, *participant))

    def fetch_match_data(self, match_id):
        match_data = self._fetch_match(match_id)
        if not match_data:
            raise DatabaseMissingRowException("Matches", "MatchID", match_id)
        participant_data = self._fetch_participants(match_id)
        return match_data, participant_data

    def _fetch_match(self, match_id):
        with DatabaseConnectionWrapper(self) as cursor:
            cursor.execute("SELECT * FROM Matches WHERE MatchID=?", (match_id,))
            match_data = cursor.fetchone()
        return match_data

    def _fetch_participants(self, match_id):
        with DatabaseConnectionWrapper(self) as cursor:
            cursor.execute("SELECT ParticipantID, Team, FrozenElo FROM Participants WHERE MatchID=?", (match_id,))
            participants = cursor.fetchall()
        return participants

    def change_user_elo(self, user_id, game, change):
        original_elo = self.fetch_user_elo(user_id, game)
        new_elo = _ensure_elo_change_valid(original_elo, change)
        self._update_user_elo(user_id, game, new_elo)

    def _update_user_elo(self, user_id, game, new_elo):
        _validate_updated_elo(new_elo)
        with DatabaseConnectionWrapper(self) as cursor:
            cursor.execute("UPDATE UserElos SET Elo=? WHERE Snowflake=? AND Game=?", (new_elo, user_id, game))

    def fetch_user_elo(self, user_id, game):
        self._assert_elo_exists(user_id, game)
        with DatabaseConnectionWrapper(self) as cursor:
            cursor.execute("SELECT Elo FROM UserElos WHERE Snowflake=? AND Game=?", (user_id, game))
            elo = cursor.fetchone()[0]
        return elo

    def _assert_elo_exists(self, user_id, game):
        if not self._user_elo_exists(user_id, game):
            raise DatabaseMissingRowException("UserElos", "Snowflake", user_id)

    def set_user_elo(self, user_id, game, user_elo):
        """NOTE: Very powerful, hard set with minimal validation. Use with care."""
        if self._user_elo_exists(user_id, game):
            self._update_user_elo(user_id, game, user_elo)
        else:
            self.insert_user_elo(user_id, game, user_elo)

    def _validate_alias(self, alias):
        with DatabaseConnectionWrapper(self) as cursor:
            cursor.execute("SELECT Count(*) FROM Aliases WHERE Alias=?", (alias,))
            if cursor.fetchone()[0] > 0:
                raise DatabaseDuplicateUniqueRowException("Aliases", "Alias", alias)


def _get_data_or_default(dict_entry: Dict[str, Any], key: str, default: Any):
    return dict_entry[key] if key in dict_entry else default


def _get_game_data_from_dict_item(game_item):
    game_name, game_data = game_item
    colour = _get_data_or_default(game_data, "colour", "0xffffff")
    icon = _get_data_or_default(game_data, "icon", "https://cdn.pixabay.com/photo/2012/04/24/12/43/t-39853_960_720.png")
    min_team_size = _get_data_or_default(game_data, "min_team_size", 5)
    max_team_size = _get_data_or_default(game_data, "max_team_size", min_team_size)
    team_count = _get_data_or_default(game_data, "team_count", 2)
    aliases = _get_data_or_default(game_data, "alias", [])
    return (game_name, colour, icon, min_team_size, max_team_size, team_count), aliases


def _validate_inserted_elo(elo):
    if elo < 0:
        raise BotLoggedContextException("Initial elo values cannot be lower than 0.")
    if elo > 5000:
        raise BotLoggedContextException("Initial elo values cannot be higher than 5000.")


def _ensure_elo_change_valid(original_elo, change):
    return 0 if original_elo + change < 0 else original_elo + change


def _validate_updated_elo(new_elo):
    if new_elo < 0:
        raise BotLoggedContextException("User elo value cannot be lower than 0.")


# Enable initializing the database without starting the bot by making this file executable and running the
# initialization logic on execution
if __name__ == "__main__":  # pragma: no cover
    init_manager = GamesDatabaseManager()
    init_manager.setup_manager()
