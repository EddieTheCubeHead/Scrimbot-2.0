__version__ = "0.2"
__author__ = "Eetu Asikainen"

from unittest.mock import MagicMock, AsyncMock

from discord import VoiceChannel

from Src.Bot.Cogs.Helpers.ScrimVoiceOperationService import ScrimVoiceOperationService
from Src.Bot.DataClasses.Team import Team
from Utils.TestBases.AsyncUnittestBase import AsyncUnittestBase
from Utils.TestHelpers.TestIdGenerator import TestIdGenerator


class TestScrimVoiceOperationService(AsyncUnittestBase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.id_generator = TestIdGenerator()

    def setUp(self) -> None:
        self.player_states: dict[int, MagicMock] = {}
        self.channels: dict[int, VoiceChannel] = {}
        self.service = ScrimVoiceOperationService()
        self.guild = AsyncMock()
        self.guild.id = self.id_generator.generate_viable_id()
        self.team_voices = [MagicMock(), MagicMock()]
        self.scrim = MagicMock()
        self.scrim.teams = self._create_teams()
        self.guild.get_member.side_effect = lambda player_id: self.player_states[player_id]
        self.guild.get_channel.side_effect = lambda channel_id: self.channels[channel_id]

    async def test_try_move_to_voice_given_all_players_present_then_returns_true(self):
        self.assertTrue(await self.service.try_move_to_voice(self.guild, self.scrim))

    async def test_try_move_to_voice_given_all_players_present_then_gets_all_players_and_moves_them(self):
        await self.service.try_move_to_voice(self.guild, self.scrim)
        for participant_team in self.scrim.teams:
            for player in participant_team.team.members:
                member = self.player_states[player.user_id]
                member.move_to.assert_called_with(self.channels[participant_team.team.channel_id])

    async def test_try_move_to_void_given_not_all_players_present_then_returns_false(self):
        for index, player_state in enumerate(self.player_states, 1):
            with self.subTest(f"Attempt moving to voice with player not in voice: player {index}"):
                temp_state = self.player_states[player_state].voice
                self.player_states[player_state].voice = None
                self.assertFalse(await self.service.try_move_to_voice(self.guild, self.scrim))
                self.player_states[player_state].voice = temp_state

    def _create_teams(self, team_amount: int = 2, team_size: int = 5) -> list[Team]:
        teams = []
        for team_num in range(1, team_amount + 1):
            team = MagicMock()
            team.channel_id = self.id_generator.generate_viable_id()
            team.name = f"Team {team_num}"
            team.members = []
            participant_team = MagicMock()
            for _ in range(team_size):
                team.members.append(self._create_member())
            participant_team.team = team
            teams.append(participant_team)
            self.channels[team.channel_id] = MagicMock()
        return teams

    def _create_member(self, voice_present: bool = True):
        member = AsyncMock()
        member.user_id = self.id_generator.generate_viable_id()
        if not voice_present:
            member.voice = None
        else:
            member.voice.channel.guild.id = self.guild.id
        self.player_states[member.user_id] = member
        return member
