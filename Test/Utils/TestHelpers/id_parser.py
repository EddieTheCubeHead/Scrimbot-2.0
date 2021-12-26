__version__ = "0.1"
__author__ = "Eetu Asikainen"

import os
import re


def insert_ids(context, message):
    processed = message
    while inserted := re.search(r"(\{\w+\}|\{\\n\})", processed):
        if inserted.group() == r"{\n}":
            data = os.linesep
        else:
            data = context.discord_ids[inserted.group()[1:-1]]
        insert_start, insert_end = inserted.span()
        processed = processed[:insert_start] + str(data) + processed[insert_end:]
    return processed
