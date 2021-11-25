__version__ = "ver"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock

from Bot.EmbedSystem.ExceptionEmbedBuilder import ExceptionEmbedBuilder
from Utils.TestBases.EmbedUnittest import EmbedUnittest


class TestExceptionEmbedBuilder(EmbedUnittest):

    def setUp(self) -> None:
        self.embed_builder = ExceptionEmbedBuilder()
        self.ctx = MagicMock()
        self.ctx.command = MagicMock()
        self.ctx.command.name = "test"
        self.ctx.message.content = ";test args"
        self.ctx.prefix = ";"

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_dependency(ExceptionEmbedBuilder)

    def test_build_given_exception_with_message_and_no_help_then_embed_built_correctly(self):
        exception = MagicMock()
        exception.message = "Test exception"
        exception.send_help = False
        embed = self.embed_builder.build(self.ctx, exception)
        self.assertEqual("ScrimBot Error", embed.title)
        self.assertEqual("An error happened while processing command 'test'", embed.description)
        self.assertEqual("If you think this behaviour is unintended, please report it in the bot repository in GitHub "
                         "at https://github.com/EddieTheCubeHead/Scrimbot-2.0", embed.footer.text)
        self._assert_correct_fields(embed, ("Error message:", "Test exception"))

    def test_build_given_exception_with_message_and_help_required_then_embed_built_correctly(self):
        exception = MagicMock()
        exception.message = "Test exception"
        exception.get_help_portion.return_value = ";help test"
        embed = self.embed_builder.build(self.ctx, exception)
        self.assertEqual("ScrimBot Error", embed.title)
        self.assertEqual("An error happened while processing command 'test'", embed.description)
        self.assertEqual("If you think this behaviour is unintended, please report it in the bot repository in GitHub "
                         "at https://github.com/EddieTheCubeHead/Scrimbot-2.0", embed.footer.text)
        self._assert_correct_fields(embed, ("Error message:", "Test exception"), ("To get help:", ";help test"))
