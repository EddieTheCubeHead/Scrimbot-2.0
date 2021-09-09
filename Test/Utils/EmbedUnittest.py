__version__ = "0.1"
__author__ = "Eetu Asikainen"

from discord import Embed

from Utils.UnittestBase import UnittestBase


class EmbedUnittest(UnittestBase):

    def _assert_correct_fields(self, embed: Embed, *field_data: (str, str)):
        for index, field in enumerate(field_data):
            self.assertEqual(field[0], embed.fields[index].name)
            self.assertEqual(field[1], embed.fields[index].value)

