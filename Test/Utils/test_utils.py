__version__ = "0.1"
__author__ = "Eetu Asikainen"

import os
import re
import unittest
from pathlib import Path
from typing import Tuple, Type, Optional


def assert_tuple_with_correct_types(actual: Tuple, *tuple_fields: Type) -> Optional[str]:
    if len(actual) != len(tuple_fields):
        return f"Expected a tuple with length of {len(tuple_fields)}, actual length was {len(actual)}!"
    for actual, expected in zip(actual, tuple_fields):
        if not isinstance(actual, expected):
            return f"Expected an instance of {expected}, got an instance of {type(actual)}."


def get_cogs_messages():
    root = str(Path(os.path.join(os.path.dirname(__file__))).parent.parent.absolute())
    for cog in os.listdir(rf"{root}\Src\Bot\Cogs"):
        if re.match(r"^[^_][a-zA-Z]*\.py$", cog):
            yield rf"Using cog Bot.Cogs.{cog[:-3]}, with version {__version__}"
