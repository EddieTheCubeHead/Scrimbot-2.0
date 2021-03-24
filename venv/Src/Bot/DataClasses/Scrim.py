__version__ = "0.1"
__author__ = "Eetu Asikainen"

import datetime

import discord
from discord.ext import commands

from Src.Bot.DataClasses.ScrimState import ScrimState
from Src.Bot.DataClasses.ScrimTeam import ScrimTeam
from Src.Bot.DataClasses.Game import Game
from Src.Bot.DataClasses.ScrimEmbed import ScrimEmbed
from Src.Database.DatabaseManager import DatabaseManager

class Scrim():

    _all_scrims = {}
    _all_participants = set()
    _db_manager = None

    def __init__(self, channel: discord.TextChannel, team_1_voice: discord.VoiceChannel = None,
                 team_2_voice: discord.VoiceChannel = None, spectator_voice: discord.VoiceChannel = None):

        self._channel = channel
        self._team_1_voice = team_1_voice
        self._team_2_voice = team_2_voice
        self._spectator_voice = spectator_voice

        # The reset function just sets all values to 0/Null/etc. so it can be used to init the class
        self.reset()

        self._all_scrims[channel.id] = self

    @classmethod
    async def get_scrim(cls, ctx: commands.Context):

        if ctx.channel.id not in cls._all_scrims:
            db_entry = cls._db_manager.fetch_scrim(ctx.channel.id)
            if not db_entry:
                raise commands.BadArgument("This channel is not registered for scrim usage.")
            else:
                channel = ctx.channel
                team_1_voice, team_2_voice, spectator_voice = None, None, None
                if len(db_entry) >= 3:
                    team_1_voice = ctx.guild.get_channel(db_entry[1])
                    team_2_voice = ctx.guild.get_channel(db_entry[2])
                if len(db_entry) >= 4:
                    spectator_voice = ctx.guild.get_channel(db_entry[3])

                return Scrim(channel, team_1_voice, team_2_voice, spectator_voice)
        
        else:
            cls._all_scrims[ctx.channel.id].last_interaction = datetime.datetime.now()
            return cls._all_scrims[ctx.channel.id]

    @classmethod
    async def get_from_reaction(cls, react: discord.reaction):
        if react.message.channel.id not in cls._all_scrims:
            return

        else:
            scrim = cls._all_scrims[react.message.channel.id]

            if react.message == scrim._message:
                return Scrim
        return

    @classmethod
    def set_database_manager(cls, manager: DatabaseManager):
        cls._db_manager = manager

    @classmethod
    def tick_all(cls):
        for scrim in cls._all_scrims.items():
            scrim._tick()

    def _tick(self):
        idle_time = datetime.datetime.now() - self._last_interaction

        # The bot will be run on a raspberry pi, this will cleanup the scrim list if some scrim channels become unactive
        if idle_time >= datetime.timedelta(days=30):
            if self.state != ScrimState.INACTIVE:
                self.terminate("Terminated due to inactivity.")
            self._all_scrims.pop(self._channel.id)

        if self._deletion_time and idle_time >= datetime.timedelta(seconds=self._deletion_time*60):
            self.terminate()

    async def _update_embed(self):
        pass

    def _create_player_list(self, team: ScrimTeam):
        if team == ScrimTeam.TEAMLESS:
            return "\n".join([discord.utils.escape_markdown(user.nick or user.name) for user in self._participants])

        elif team == ScrimTeam.SPECTATOR:
            return "\n".join([discord.utils.escape_markdown(user.nick or user.name) for user in self._spectators])

        else:
            player_list = self._team_1 if team == ScrimTeam.TEAM1 else self._team_2
            string_list = [discord.utils.escape_markdown(user.nick or user.name) for user in player_list]

            # Bolding captains
            if string_list and self.state == ScrimState.CAPS:
                string_list[0] = "**" + string_list[0] + "**"

            return "\n".join(string_list)



    async def create(self, ctx: commands.Context, game: Game, deletion_time: int,
                     is_ranked: bool = True):
        self._game = game
        self._deletion_time = deletion_time
        self._embed = ScrimEmbed(game, is_ranked)

        self.master = ctx.author
        self.state = ScrimState.LFP

        self._message = await ctx.send(embed=self._embed)
        await self._message.add_reaction(emoji="\U0001F3AE")  # video game controller
        await self._message.add_reaction(emoji="\U0001F441")  # eye

    async def add_player(self, player: discord.Member):
        if self.state != ScrimState.LFP or player in self._all_participants:
            return

        self._participants.append(player)
        self._all_participants.add(player)

        await self._update_embed()

    async def terminate(self, reason: str):
        self._embed.terminate(reason)
        await self._message.edit(embed=self._embed)
        await self._message.clear_reactions()
        self.reset()

    def reset(self):
        self.state = ScrimState.INACTIVE

        self._last_interaction = datetime.now()
        self._deletion_time = 0

        self._game = None
        self.master = None
        self._message = None
        self._embed = None
        self._cap_1 = None
        self._cap_2 = None

        self._participants = []
        self._team_1 = []
        self._team_2 = []
        self._spectators = []
