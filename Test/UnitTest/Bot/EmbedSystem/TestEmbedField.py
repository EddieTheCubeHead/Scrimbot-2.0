__version__ = "0.1"
__author__ = "Eetu Asikainen"

from Utils.UnittestBase import UnittestBase
from Bot.EmbedSystem.EmbedField import EmbedField


class TestEmbedField(UnittestBase):

    def test_get_name_given_valid_field_then_correct_string_returned(self):
        name, content = "Foo", "Bar"
        field = EmbedField(name, content, True)
        self.assertEqual(name, field.get_name())

    def test_get_value_given_valid_field_then_correct_string_returned(self):
        name, content = "Foo", "Bar"
        field = EmbedField(name, content, True)
        self.assertEqual(content, field.get_value())
