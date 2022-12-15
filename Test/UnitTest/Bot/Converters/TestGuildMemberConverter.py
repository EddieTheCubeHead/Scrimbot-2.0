__version__ = "ver"
__author__ = "Eetu Asikainen"

from unittest.mock import AsyncMock, MagicMock, patch

from Src.Bot.Converters.GuildMemberConverter import GuildMemberConverter
from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestGuildMemberConverter(AsyncUnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_mocker = TestIdGenerator()

    def setUp(self) -> None:
        self.discord_convert = AsyncMock()
        self.connection = MagicMock()
        self.context = MagicMock()
        self.context.guild.id = self.id_mocker.generate_viable_id()
        self.converter = GuildMemberConverter(self.connection)

    def test_build_given_file_imported_then_singleton_dependency_created(self):
        self._assert_singleton_dependency(GuildMemberConverter)

    async def test_convert_given_called_with_new_member_then_discord_converter_called_and_new_member_returned(self):
        mock_guild_member = MagicMock()
        mock_guild_member.id = self.id_mocker.generate_viable_id()
        self.connection.get_guild_member.return_value = mock_guild_member
        self.discord_convert.return_value = mock_guild_member
        with patch("discord.ext.commands.converter.MemberConverter.convert", self.discord_convert):
            actual_user = await self.converter.convert(self.context, str(mock_guild_member.id))
        self.assertEqual(mock_guild_member, actual_user)
        self.connection.get_guild_member.assert_called_with(mock_guild_member.id, self.context.guild.id)

    async def test_convert_when_called_then_discord_member_added_to_the_user(self):
        mock_guild_member = MagicMock()
        mock_discord_member = MagicMock()
        mock_discord_member.id = self.id_mocker.generate_viable_id()
        self.discord_convert.return_value = mock_discord_member
        with patch("discord.ext.commands.converter.MemberConverter.convert", self.discord_convert):
            actual_user = await self.converter.convert(self.context, str(mock_guild_member.id))
        self.assertEqual(mock_discord_member, actual_user.member)
        self.connection.get_guild_member.assert_called_with(mock_discord_member.id, self.context.guild.id)

    def test_get_user_given_called_with_user_id_then_user_returned(self):
        mock_guild_member = MagicMock()
        mock_guild_member.id = self.id_mocker.generate_viable_id()
        self.connection.get_guild_member.return_value = mock_guild_member
        actual_user = self.converter.get_guild_member(mock_guild_member.id, self.context.guild.id)
        self.assertEqual(mock_guild_member, actual_user)
        self.connection.get_guild_member.assert_called_with(mock_guild_member.id, self.context.guild.id)
