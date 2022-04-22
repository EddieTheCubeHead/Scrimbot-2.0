__version__ = "0.1"
__author__ = "Eetu Asikainen"

import os
import re
from re import Match

from behave.runner import Context

from Test.Utils.TestHelpers.TestIdGenerator import GLOBAL_ID_GENERATOR


class UserListMatch:

    def __init__(self, *match_ids: int, amount: int = None):
        self.amount = amount if amount is not None else len(match_ids)
        self.found = 0
        self.match_ids = list(match_ids)
        self.next_id = self.match_ids.pop(0) if amount is None else None

    def __repr__(self):
        if self.amount is not None:
            return f"{self.amount} user mentions in group {self.match_ids}"
        return f"User mentions for users in {self.match_ids} in order"

    def assert_matches(self, text: str, context):
        for line in text.split(os.linesep):
            self.found += 1
            assert self.amount >= self.found, f"Found too many user id's in field {text}. (Expected {self.amount})"
            self._assert_valid_line(line, context)

    def _assert_valid_line(self, line: str, context):
        actual_id = int(_get_user_id(line))
        if self.next_id is not None:
            expected_id = try_get_id(context, f"user_{self.next_id}_id")
            assert expected_id == actual_id, f"Expected id {expected_id} but id was actually {actual_id}"
            if len(self.match_ids) > 0:
                self.next_id = self.match_ids.pop(0)
        else:
            valid_ids = [try_get_id(context, f"user_{user_id}_id") for user_id in self.match_ids]
            assert actual_id in valid_ids, f"Expected to find id {actual_id} in {valid_ids}"


def process_inserts(context, message):
    user_list_match = _match_user_list(message)
    if user_list_match:
        return _parse_user_listing(user_list_match)
    processed = message
    while inserted := re.search(r"(\{\w+\}|\{\\n\})", processed):
        processed = _try_replace(context, inserted, processed)
    return processed


def _match_user_list(message: str):
    return re.match(r"^{{((\d*) users? in |)users? ([^\{\}]*)}}$", message)


def _parse_user_listing(match: Match) -> UserListMatch:
    amount_group = None if match.group(1) is None else match.group(2)
    amount = None
    if amount_group is not None:
        amount = int(amount_group)
    users = parse_player_spec(None, match.group(3))
    return UserListMatch(*users, amount=amount)


def _try_replace(context: Context, inserted: re.Match, processed: str):
    if inserted.group() == r"{\n}":
        data = os.linesep
    else:
        data = context.discord_ids[inserted.group()[1:-1]]
    insert_start, insert_end = inserted.span()
    processed = processed[:insert_start] + str(data) + processed[insert_end:]
    return processed


def parse_player_spec(context, player_spec) -> list[int]:
    if "all" in player_spec:
        return []
    player_spec = player_spec.replace("players ", "")
    player_spec = player_spec.replace("player ", "")
    if "to" in player_spec:
        start, stop = player_spec.split(" to ")
        player_nums = list(range(int(start), int(stop) + 1))
    else:
        player_spec = player_spec.replace(" and", ",")
        player_nums = [int(num) for num in player_spec.split(", ") if num.isdigit()]
    if context:
        return [try_get_id(context, f"user_{player_num}_id") for player_num in player_nums]
    return player_nums


def get_id_increment(context: Context, id_type: str) -> int:
    id_increment = 1
    while f"{id_type}_{id_increment}_id" in context.discord_ids:
        id_increment += 1
    return id_increment


def try_get_id(context, id_string):
    mock_id = context.discord_ids.pop(id_string, GLOBAL_ID_GENERATOR.generate_viable_id())
    context.discord_ids[id_string] = mock_id
    return mock_id


def _get_user_id(line: str):
    match = re.match(r"^<@(\d*)>(| \*\*C\*\*)$", line)
    assert match, f"Line {line} does not contain a user entry"
    return match.group(1)
