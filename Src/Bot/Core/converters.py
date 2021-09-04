__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Src.Bot.Exceptions.BotBaseUserException import BotBaseUserException


def parse_winner(argument: str) -> int:
    """A converter that parses a string into an int representing the team that won (0 represents a tie)."""

    if argument in ("1", "One", "one", "Team1", "team1", "Team 1", "team 1"):
        return 1
    if argument in ("2", "Two", "two", "Team2", "team2", "Team 2", "team 2"):
        return 2
    if argument in ("0", "Tie", "tie", "Draw", "draw", "None", "none"):
        return 0
    raise BotBaseUserException(f"Couldn't parse team from string '{argument}'. "
                               "Please give winner as '1', '2' or 'tie'.")
