from __future__ import annotations

__version__ = "0.1"
__author__ = "Eetu Asikainen"

import datetime
import asyncio
from typing import Optional

import discord
from discord.ext import commands

from Src.Bot.DataClasses.ScrimState import ScrimState
from Src.Bot.DataClasses.Game import Game
from Src.Bot.DataClasses.ScrimEmbed import ScrimEmbed
from Src.Database.DatabaseManager import DatabaseManager

class Scrim():
    """A class that houses data storage and implements data manipulation methods for the scrims themselves

    params
    ------
    state: ScrimState
        An enum value for state handling

    classmethods
    ------------
    get_scrim(ctx)
        Fetches or creates a scrim from a compatible command invokation context

    get_from_reaciton(react)
        Fetches a scrim from a discord reaction event

    set_database_manager(manager)
        Used to initialise the shared database manager used by the whole application

    tick_all()
        A method for ticking all existing scrims (see method _tick)

    methods
    -------
    create(ctx, game, deletion_time, is_ranked = True)
        A method for creating a new scrim on the channel corresponding to the current instance of the class

    add_player(player)
        A method for adding a player as a participant to a scrim

    remove_player(player)
        A method for removing a participant from a scrim

    add_spectator(spectator)
        A method for adding a spectator to a scrim

    remove_spectator(spectator)
        A method for removing a spectator from a scrim

    lock()
        A method that locks the current players and ends the 'looking for players' phase of a scrim

    terminate(reason)
        A method to forcefully terminate the current scrim

    reset()
        A method for resetting the values back to nulls/empty values after a scrim has been concluded.
    """

    _all_scrims = {}
    _all_participants = set()
    _all_participant_lock = asyncio.Lock()
    _db_manager = None

    def __init__(self, channel: discord.TextChannel, team_1_voice: discord.VoiceChannel = None,
                 team_2_voice: discord.VoiceChannel = None, spectator_voice: discord.VoiceChannel = None):
        """A constructor for the Scrim class

        args
        ----

        :param channel: The text channel the scrim is registered to
        :type channel: discord.TextChannel
        :param team_1_voice: The voice channel assigned to team 1
        :type team_1_voice: Optional[discord.VoiceChannel]
        :param team_2_voice: The voice channel assigned to team 2
        :type team_2_voice: Optional[discord.VoiceChannel]
        :param spectator_voice: The voice channel assigned to spectators
        :type spectator_voice: Optional[discord.VoiceChannel]
        """

        self._channel = channel
        self._team_1_voice = team_1_voice
        self._team_2_voice = team_2_voice
        self._spectator_voice = spectator_voice

        self._participants = []
        self._spectators = []
        self._team_1 = []
        self._team_2 = []
        self.master = None

        self._team_1_lock = asyncio.Lock()
        self._team_2_lock = asyncio.Lock()

        self.state = ScrimState.INACTIVE
        self._last_interaction = datetime.datetime.now()

        self._all_scrims[channel.id] = self

    @classmethod
    async def get_scrim(cls, ctx: commands.Context) -> Scrim:
        """A classmethod for fetching a scrim based on a ctx object or creating a new instance if needed and appropiate

        args
        ----

        :param ctx: The invokation context of the command requiring a scrim
        :type ctx: commands.Context
        :return: A scrim instance based on a registered text channel
        :rtype: Scrim
        :raises: commands.BadArgument
        """

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
    async def get_from_reaction(cls, react: discord.reaction) -> Optional[Scrim]:
        """A classmethod for fetching a scrim

        args
        ----

        :param react: The reaction based on which to fetch the scrim
        :type react: discord.reaction
        :return: A scrim corresponding to the given reaction
        :rtype: Scrim
        """

        if react.message.channel.id not in cls._all_scrims:
            return

        else:
            scrim: Scrim = cls._all_scrims[react.message.channel.id]

            if react.message == scrim._message:
                scrim._last_interaction = datetime.datetime.now()
                return scrim
        return

    @classmethod
    def set_database_manager(cls, manager: DatabaseManager):
        """A classmethod for setting the shared database manager used for fetching scrims

        args
        ----

        :param manager: The database manager used by the rest of the app
        :type manager: DatabaseManager
        """

        cls._db_manager = manager

    @classmethod
    async def tick_all(cls):
        """A classmethod for ticking all existing scrim instances"""
        for scrim in cls._all_scrims.items():
            await scrim._tick()

    async def _tick(self):
        """A private methdod for ticking a scrim instance, terminating idle scrims and deleting old instances"""

        idle_time = datetime.datetime.now() - self._last_interaction

        # The bot will be run on a raspberry pi, this will cleanup the scrim list if some scrim channels become inactive
        if idle_time >= datetime.timedelta(days=30):
            if self.state != ScrimState.INACTIVE:
                await self.terminate("Terminated due to inactivity.")
            self._all_scrims.pop(self._channel.id)

        if self._deletion_time and idle_time >= datetime.timedelta(seconds=self._deletion_time*60):
            await self.terminate()

    async def create(self, ctx: commands.Context, game: Game, deletion_time: int,
                     is_ranked: bool = True):
        """A method that creates a new scrim on an active and registred channel.

        args
        ----

        :param ctx: The invokation context of the command creating the scrim
        :type ctx: commands.Context
        :param game: The game of the scrim
        :type game: Game
        :param deletion_time: How long the scrim can be inactive before getting automatically terminated. 0 = infinitely
        :type deletion_time: int
        :param is_ranked: Whether the scrim should update the bot's matchmaking ratings
        :type is_ranked: bool
        """

        self._game = game
        self._deletion_time = deletion_time
        self._embed = ScrimEmbed(game, is_ranked)

        self.master = ctx.author
        self.state = ScrimState.LFP

        self._message = await ctx.send(embed=self._embed)
        await self._message.add_reaction(emoji="\U0001F3AE")  # video game controller
        await self._message.add_reaction(emoji="\U0001F441")  # eye

    async def add_player(self, player: discord.Member):
        """A method for adding a player to the participants of a scrim

        args
        ----

        :param player: The player to be added
        :type player: discord.Member
        """

        if self.state != ScrimState.LFP:
            return

        async with self._all_participant_lock:
            if player.id in self._all_participants:
                raise commands.BadArgument("Cannot join more than one scrim at a time.")

            self._participants.append(player.id)
            self._all_participants.add(player.id)
            self._embed.add_to_participants(player.id, discord.utils.escape_markdown(player.display_name))

            await self._message.edit(embed=self._embed)

    async def remove_player(self, player: discord.Member):
        """A method for removing a player from the participants of a scrim

        args
        ----

        :param player: The player to be removed
        :type player: discord.Member
        """

        if self.state != ScrimState.LFP:
            return

        async with self._all_participant_lock:
            if player.id not in self._participants:
                return

            self._participants.remove(player.id)
            self._all_participants.remove(player.id)
            self._embed.remove_from_participants(player.id)

            await self._message.edit(embed=self._embed)

    async def add_spectator(self, spectator: discord.Member):
        """A method for adding a user to the spectators of a scrim

        args
        ----

        :param spectator: The user to be added
        :type spectator: discord.Member
        """

        if self.state != ScrimState.LFP:
            return

        async with self._all_participant_lock:
            if spectator.id in self._participants:
                raise commands.BadArgument("Cannot spectate a scrim you are participating in.")

            self._spectators.append(spectator.id)
            self._embed.add_to_spectators(spectator.id, discord.utils.escape_markdown(spectator.display_name))

            await self._message.edit(embed=self._embed)

    async def remove_spectator(self, spectator: discord.Member):
        """A method for removing a user from the spectators of a scrim

        args
        ----

        :param spectator: The user to be removed
        :type spectator: discord.Member
        """

        if self.state != ScrimState.LFP:
            return

        if spectator.id not in self._spectators:
            return

        self._spectators.remove(spectator.id)
        self._embed.remove_from_spectators(spectator.id)

        await self._message.edit(embed=self._embed)

    async def lock(self):
        """A method for locking a full scrim, preventing manipulation of participants and starting the team selection"""

        if len(self._participants) < self._game.playercount:
            error_str = f"Need {self._game.playercount - len(self._participants)} more players to lock the scrim."
            raise commands.CommandError(error_str)
        self._participants = self._participants[:self._game.playercount]
        self._embed.lock_scrim()
        await self._message.edit(embed=self._embed)
        await self._message.clear_reactions()
        await self._message.add_reaction("1\u20E3")
        await self._message.add_reaction("1\u20E3")

    async def terminate(self, reason: str):
        """A method for terminating an ongoing scrim prematurely

        args
        ----

        :param reason: The reason for the termination that will be displayed to the users
        :type reason: str
        """

        self._embed.terminate(reason)
        await self._message.edit(embed=self._embed)
        await self._message.clear_reactions()
        async with self._all_participant_lock:
            self._all_participants.difference_update({*self._participants, *self._team_1, *self._team_2})
        self.reset()

    def reset(self):
        """A method for resetting the values of the scrim to ensure problem-free termination"""

        self.state = ScrimState.INACTIVE

        self._last_interaction = datetime.datetime.now()
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
