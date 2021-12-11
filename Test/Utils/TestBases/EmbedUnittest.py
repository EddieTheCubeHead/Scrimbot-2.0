__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import Optional

from discord import Embed

from Utils.TestBases.UnittestBase import UnittestBase


class EmbedUnittest(UnittestBase):

    def _assert_correct_fields(self, embed: Embed, *field_data: (str, str, Optional[bool])):
        self.assertEqual(len(field_data), len(embed.fields), f"Expected {len(field_data)} fields but found "
                                                             f"{len(embed.fields)} instead.")
        for expected, actual in zip(field_data, embed.fields):
            self.assertEqual(expected[0], actual.name)
            self.assertEqual(expected[1], actual.value)
            if len(expected) > 2:
                self.assertEqual(expected[2], actual.inline)

