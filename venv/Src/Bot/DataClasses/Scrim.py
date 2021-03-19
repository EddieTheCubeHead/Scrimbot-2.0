__version__ = "0.1"
__author__ = "Eetu Asikainen"

import discord
from discord.ext import commands

from Src.Bot.DataClasses.ScrimState import ScrimState
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
            cls._all_scrims[ctx.channel.id].last_interaction = 0
            return cls._all_scrims[ctx.channel.id]

    @classmethod
    def set_database_manager(cls, manager: DatabaseManager):
        cls._db_manager = manager

    @classmethod
    def tick_all(cls):
        for scrim in cls._all_scrims.items():
            scrim._tick()

    def _tick(self):
        if self.state == ScrimState.LFP:
            self._last_interaction += 1

            if self._deletion_time and self._last_interaction >= self._deletion_time:
                self.terminate()

    def terminate(self):
        self._embed.terminate()
        self.reset()

    def reset(self):
        self.state = ScrimState.INACTIVE

        self._last_interaction = 0
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

    async def create(self, ctx: commands.Context, game: Game, deletion_time: int,
                     is_ranked: bool = True):
        self._game = game
        self._master = ctx.author
        self._deletion_time = deletion_time
        self._embed = ScrimEmbed(game, is_ranked)
        self._state = ScrimState.LFP

        self._message = await ctx.send(embed=self._embed)
