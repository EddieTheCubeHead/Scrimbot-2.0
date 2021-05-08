from __future__ import annotations

__version__ = "0.1"
__author__ = "Eetu Asikainen"

import datetime
import asyncio
from typing import Optional, Dict, Set, List

import discord
from discord.ext import commands

from Src.Bot.DataClasses.ScrimState import ScrimState
from Src.Bot.DataClasses.Game import Game
from Src.Bot.DataClasses.ScrimEmbed import ScrimEmbed
from Src.Bot.DataClasses.ScrimTeam import ScrimTeam
from Src.Bot.DataClasses.EmbedField import EmbedField
from Src.Bot.Exceptions.BotMissingScrimException import BotMissingScrimException
from Src.Bot.Exceptions.BotBaseInternalException import BotBaseInternalException
from Src.Bot.Exceptions.BotBaseUserException import BotBaseUserException
from Src.Database.DatabaseManager import DatabaseManager


class Scrim:
    """A class that houses data storage and implements data manipulation methods for the scrims themselves

    attributes
    ----------

    state: ScrimState
        An enum value for state handling

    master: discord.Member
        The user who created the scrim. Used for some checks

    classmethods
    ------------

    get_scrim(ctx) -> Scrim
        Fetches or creates a scrim from a compatible command invocation context

    get_from_reaction(react) -> Optional[Scrim]
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

    set_team_1(player)
        A method to set a player's team as team 1

    set_team_2(player)
        A method to set a player's team as team 2

    set_teamless(player)
        A method to set a player as belonging to neither team

    start()
        A method to start a scrim if both teams are full

    finish(winner)
        A method to finish a scrim, declare winner and update and save corresponding statistics

    terminate(reason)
        A method to forcefully terminate the current scrim

    reset()
        A method for resetting the values back to nulls/empty values after a scrim has been concluded.
    """

    _all_scrims: Dict[str, Scrim] = {}
    _all_participants: Set[discord.Member] = set()
    _all_participant_lock: asyncio.Lock = asyncio.Lock()
    _db_manager: DatabaseManager = None

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

        self._channel: discord.TextChannel = channel
        self._team_1_voice: Optional[discord.VoiceChannel] = team_1_voice
        self._team_2_voice: Optional[discord.VoiceChannel] = team_2_voice
        self._spectator_voice: Optional[discord.VoiceChannel] = spectator_voice

        self.master: Optional[discord.Member] = None

        self._teams_lock: asyncio.Lock = asyncio.Lock()  # Lock for updating teams
        self._embed_lock: asyncio.Lock = asyncio.Lock()  # Lock for updating the embed
        self._state_change_lock: asyncio.Lock = asyncio.Lock()  # Lock for commands causing state changes

        self.state: ScrimState = ScrimState.INACTIVE
        self._last_interaction: datetime.datetime = datetime.datetime.now()

        self._all_scrims[channel.id] = self

        self._game: Optional[Game] = None
        self._deletion_time: int = 0

        self._participants: Optional[ScrimTeam] = None
        self._spectators: Optional[ScrimTeam] = None
        self._queue: Optional[ScrimTeam] = None

        self._embed: Optional[ScrimEmbed] = None
        self._message: Optional[discord.Message] = None

        self._cap_1: Optional[discord.Member] = None
        self._cap_2: Optional[discord.Member] = None

        self._team_1: Optional[ScrimTeam] = None
        self._team_2: Optional[ScrimTeam] = None

        div_string = "------------------------------------------------------------"
        self._divider: EmbedField = EmbedField(div_string, div_string, False)

    @classmethod
    async def get_scrim(cls, ctx: commands.Context) -> Scrim:
        """A classmethod for fetching a scrim based on a ctx object or creating a new instance if needed and appropiate

        args
        ----

        :param ctx: The invocation context of the command requiring a scrim
        :type ctx: commands.Context
        :return: A scrim instance based on a registered text channel
        :rtype: Scrim
        :raises: commands.BadArgument
        """

        if ctx.channel.id not in cls._all_scrims:
            db_entry = cls._db_manager.fetch_scrim(ctx.channel.id)
            if not db_entry:
                raise BotMissingScrimException(ctx)
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
            cls._all_scrims[ctx.channel.id]._last_interaction = datetime.datetime.now()
            return cls._all_scrims[ctx.channel.id]

    @classmethod
    async def get_from_reaction(cls, react: discord.Reaction) -> Optional[Scrim]:
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
        for scrim in cls._all_scrims.values():
            await scrim._tick()

    async def _tick(self):
        """A private method for ticking a scrim instance, terminating idle scrims and deleting old instances"""

        idle_time = datetime.datetime.now() - self._last_interaction

        # The bot will be run on a raspberry pi, this will cleanup the scrim list if some scrim channels become inactive
        if idle_time >= datetime.timedelta(days=30):
            if self.state != ScrimState.INACTIVE:
                await self.terminate("Terminated due to inactivity.")
            self._all_scrims.pop(self._channel.id)

        if self._deletion_time and idle_time >= datetime.timedelta(seconds=self._deletion_time * 60):
            await self.terminate("Terminated due to inactivity.")

    async def _secure_state_change(self, new_state: ScrimState, *eligible_states: ScrimState):
        """A private helper method for making sure the state of the scrim changes in a thread safe way

        args
        ----

        :param new_state: The desired new state of the scrim
        :type new_state: ScrimState
        :param eligible_states: All states from which the state into the desired new state can happen (greedy)
        :type eligible_states: list[ScrimState]
        """

        async with self._state_change_lock:
            if self.state not in eligible_states:
                raise BotBaseUserException("You cannot use that now: scrim is not in the correct state.",
                                           send_help=False)

            self.state = new_state

    async def _update_embed_fields(self):
        """A private helper method that updates the embed's player list fields according to internal state and lists"""

        async with self._embed_lock:
            if self.state == ScrimState.LFP:
                self._embed.update_participants(self._participants, self._spectators, self._queue)
            elif self.state in (ScrimState.LOCKED, ScrimState.CAPS_PREP, ScrimState.CAPS):
                self._embed.update_teams(self._participants, self._spectators, self._divider, self._team_1,
                                         self._team_2)
            else:
                raise BotBaseInternalException("scrim._update_embed_fields called with weird state.")

            await self._message.edit(embed=self._embed)

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

        await self._secure_state_change(ScrimState.LFP, ScrimState.INACTIVE)

        self._game: Game = game
        self._deletion_time: int = deletion_time

        self._participants = ScrimTeam.from_team_data(game.playercount, "Players")
        self._spectators = ScrimTeam.from_team_data(0, "Spectators")
        self._queue = ScrimTeam.from_team_data(0, "Queue")
        self._queue.inline = False

        self.master = ctx.author

        async with self._embed_lock:
            self._embed: ScrimEmbed = ScrimEmbed(game, is_ranked, self._participants, self._spectators)
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
            if player in self._all_participants:
                raise commands.BadArgument("Cannot join more than one scrim at a time.")

            if self._participants.is_full():
                self._queue.append(player)
            else:
                self._participants.append(player)

            self._all_participants.add(player)

        await self._update_embed_fields()

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
            if player not in (self._participants + self._queue):
                return

            self._participants.blind_remove(player)
            self._queue.blind_remove(player)
            self._all_participants.remove(player)

            if self._queue and not self._participants.is_full():
                self._participants.append(self._queue.pop(0))

        await self._update_embed_fields()

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
            if spectator in self._participants:
                raise BotBaseInternalException("Cannot spectate a scrim you are participating in.", log=False)

            self._spectators.append(spectator)

        await self._update_embed_fields()

    async def remove_spectator(self, spectator: discord.Member):
        """A method for removing a user from the spectators of a scrim

        args
        ----

        :param spectator: The user to be removed
        :type spectator: discord.Member
        """

        if self.state != ScrimState.LFP:
            return

        if spectator not in self._spectators:
            return

        self._spectators.remove(spectator)

        await self._update_embed_fields()

    async def lock(self):
        """A method for locking a full scrim, preventing manipulation of participants and starting the team selection"""

        if len(self._participants) < self._game.playercount:
            error_str = f"Need {self._game.playercount - len(self._participants)} more players to lock the scrim."
            raise BotBaseUserException(error_str, send_help=False)

        await self._secure_state_change(ScrimState.LOCKED, ScrimState.LFP)

        async with self._all_participant_lock:
            self._all_participants.difference_update(self._queue)

        self._queue = None

        self._participants.name = "Unassigned"
        self._participants.max_size = 0

        max_team_size = int(self._game.playercount / 2)

        self._team_1: ScrimTeam = ScrimTeam.from_team_data(max_team_size, "Team 1", self._team_1_voice)
        self._team_2: ScrimTeam = ScrimTeam.from_team_data(max_team_size, "Team 2", self._team_2_voice)

        async with self._embed_lock:
            self._embed.lock_scrim(self._participants, self._spectators, self._divider, self._team_1, self._team_2)
            await self._message.edit(embed=self._embed)

        await self._message.clear_reactions()
        await self._message.add_reaction("1\u20E3")
        await self._message.add_reaction("2\u20E3")

    async def set_team_1(self, player: discord.Member):
        """A method for setting the given player as belonging to team 1

        args
        ----

        :param player: The player who should be moved
        :type player: discord.Member
        """

        async with self._teams_lock:
            # Had a lot of trouble with team assignment in the original bot, so some extensive error handling should be
            # healthy to iron out all the problems
            if player in self._team_1:
                raise BotBaseInternalException("Trying to add a player to team 1 who is already a member of team 1.")
            elif player not in self._participants + self._team_2:
                raise BotBaseInternalException("Trying to add a player to team 1 who doesn't exist in the scrim.")
            elif len(self._team_1) >= self._game.playercount / 2:
                raise BotBaseUserException(f"{self._team_1.name} is already full.", send_help=False)

            if player in self._team_2:
                await self._message.remove_reaction("2\u20E3", player)
                self._team_2.remove(player)
            else:
                self._participants.remove(player)
            self._team_1.append(player)

        await self._update_embed_fields()

    async def set_team_2(self, player: discord.Member):
        """A method for setting the given player as belonging to team 2

        args
        ----

        :param player: The player who should be moved
        :type player: discord.Member
        """

        async with self._teams_lock:
            # Had a lot of trouble with team assignment in the original bot, so some extensive error handling should be
            # healthy to iron out all the problems
            if player in self._team_2:
                raise BotBaseInternalException("Trying to add a player to team 2 who is already a member of team 2.")
            elif player not in self._participants + self._team_1:
                raise BotBaseInternalException("Trying to add a player to team 2 who doesn't exist in the scrim.")
            elif len(self._team_2) >= self._game.playercount / 2:
                raise BotBaseUserException(f"{self._team_2.name} is already full.", send_help=False)

            if player in self._team_1:
                await self._message.remove_reaction("1\u20E3", player)
                self._team_1.remove(player)
            else:
                self._participants.remove(player)

            self._team_2.append(player)

        await self._update_embed_fields()

    async def set_teamless(self, player: discord.Member):
        """A method for setting the given player as teamless in the scrim

        args
        ----

        :param player: The player who should be set teamless
        :type player: discord.Member
        """

        async with self._teams_lock:
            if not (self._team_1.blind_remove(player) or self._team_2.blind_remove(player)):
                raise BotBaseInternalException("Trying to remove a player from teams who isn't in either team.")

            self._participants.append(player)

        await self._update_embed_fields()

    async def start(self, context: commands.Context, move_voice: bool):
        """A method for starting a scrim with two full teams

        args
        ----

        :param context: The context of the message from which the command was called
        :type context: commands.Context
        :param move_voice: Whether to move the participants into voice channels, if available
        :type move_voice: bool
        """
        if not (len(self._team_1) == len(self._team_2) == self._game.playercount / 2):
            raise BotBaseUserException("You cannot use that now: both teams are not full.", send_help=False)

        prior_state = self.state

        await self._secure_state_change(ScrimState.VOICE_WAIT, ScrimState.LOCKED, ScrimState.CAPS)

        if move_voice and self._team_1_voice and self._team_2_voice:
            await self._move_voice_channels(context, prior_state)

        self.state = ScrimState.STARTED

        async with self._embed_lock:
            self._embed.start_scrim(self._spectators, self._divider, self._team_1, self._team_2)
            await self._message.edit(embed=self._embed)

        await self._message.clear_reactions()

    async def _move_voice_channels(self, context: commands.Context, prior_state: ScrimState):
        """A private helper method for moving all players into corresponding voice channels

        args
        ----

        :param context: The original invokation context of the start command
        :type context: commands.Context
        :param prior_state: The state the scrim was in before the attempt to start it
        :type prior_state: ScrimState
        """

        self._embed.wait_for_voice()
        await self._message.edit(embed=self._embed)

        voice_wait_start: datetime.datetime = datetime.datetime.now()

        while datetime.datetime.now() - voice_wait_start < datetime.timedelta(minutes=2):
            for player in self._team_1 + self._team_2:
                if player.voice is None:
                    break
                elif player.voice.channel is not None and not player.voice.channel.guild == context.guild:
                    break
            else:
                break

            await asyncio.sleep(1)

        else:
            async with self._embed_lock:
                self._embed.cancel_wait_for_voice()
                await self._message.edit(embed=self._embed)
            self.state = prior_state
            raise BotBaseUserException("Couldn't start the scrim."
                                       "All participants not connected after waiting for 5 minutes.", send_help=False)

        await self._team_1.move_to_voice()
        await self._team_2.move_to_voice()
        await self._spectators.move_to_voice(success_required=False)

    async def finish(self, winner: int):
        """A method for finishing a scrim (and updating and logging stats like player elo once those get implemented)

        args
        ----

        :param winner: The team that won the team (0 = tie)
        :type winner: int
        """

        await self._secure_state_change(ScrimState.INACTIVE, ScrimState.STARTED)

        async with self._embed_lock:
            self._embed.declare_winner(self._team_1, self._team_1, winner)
            await self._message.edit(embed=self._embed)

        self.reset()

    async def terminate(self, reason: str):
        """A method for terminating an ongoing scrim prematurely

        args
        ----

        :param reason: The reason for the termination that will be displayed to the users
        :type reason: str
        """

        async with self._embed_lock:
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

        self._team_1 = None
        self._team_2 = None
        self._participants = None
        self._spectators = None
