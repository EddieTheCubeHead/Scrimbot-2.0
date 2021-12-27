__version__ = "0.1"
__author__ = "Eetu Asikainen"

import os
import re

from behave.runner import Context

from Utils.TestHelpers.TestIdGenerator import GLOBAL_ID_GENERATOR


def insert_ids(context, message):
    processed = message
    while inserted := re.search(r"(\{\w+\}|\{\\n\})", processed):
        processed = _try_replace(context, inserted, processed)
    return processed


def _try_replace(context: Context, inserted: re.Match, processed: str):
    if inserted.group() == r"{\n}":
        data = os.linesep
    else:
        data = context.discord_ids[inserted.group()[1:-1]]
    insert_start, insert_end = inserted.span()
    processed = processed[:insert_start] + str(data) + processed[insert_end:]
    return processed


def get_id_increment(context: Context, id_type: str) -> int:
    id_increment = 1
    while f"{id_type}_{id_increment}_id" in context.discord_ids:
        id_increment += 1
    return id_increment


def try_get_id(context, id_string):
    mock_guild_id = context.discord_ids.pop(id_string, GLOBAL_ID_GENERATOR.generate_viable_id())
    context.discord_ids[id_string] = mock_guild_id
    return mock_guild_id
