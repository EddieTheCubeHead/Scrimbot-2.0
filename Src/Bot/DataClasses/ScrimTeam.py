__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import List, Optional
import collections

import discord

from Src.Bot.Exceptions.BotBaseUserException import BotBaseUserException
from Src.Bot.Exceptions.BotBaseInternalException import BotBaseInternalException
from Bot.DataClasses.Game import Game
from Src.Bot.DataClasses.EmbedField import EmbedField


class ScrimTeam(collections.UserList, EmbedField):
    """A class that houses the data of a team in a scrim

    attributes
    ----------

    name: str
        The name of the team. Functionality TBA but is meant to support custom team names
    """

    def __init__(self, data: List[discord.Member]):
        """The constructor of ScrimTeam

        :param data: The data to be stored in the list
        :type data: Game
        """

        super().__init__()
        self.data: List[discord.Member] = data

        self.max_size: int = 0
        self._voice_channel: Optional[discord.VoiceChannel] = None
        self.name = ""
        self.is_pickup = False
        self.winner = False
        self.inline = True

    @classmethod
    def from_scrim_data(cls, min_size: int, name: str, voice_channel: discord.VoiceChannel = None):
        """Because ScrimTeam subclasses UserList to function as a list of players this classmethod can be used as init

        :param min_size: How many players the team fits at maximum. 0 means infinite
        :type min_size: int
        :param name: The name of the team
        :type name: str
        :param voice_channel: The voice channel the team should be moved to when the scrim starts
        :type voice_channel:
        :return: A new ScrimTeam object with corresponding data attached
        :rtype: ScrimTeam
        """

        new_team = cls([])
        new_team.max_size = min_size
        new_team.name = name
        new_team._voice_channel = voice_channel

        return new_team

    def get_name(self) -> str:
        """A method for getting the name of the team formatted for embed displaying

        :return: A formatted string representing the team name
        :rtype: str
        """

        return f"**{self.name}**{self._get_state_addon()}"

    def _get_state_addon(self) -> str:
        """A private helper method that returns required addons to the team name based on team state

        :return: A string that represents the scrim state. Might be an empty string, but not None
        :rtype: str
        """

        if self.winner:
            return " _winner_"

        elif self.is_full():
            return " _(full)_"

        elif self.max_size:
            return f" _({len(self.data)}/{self.max_size})_"

        else:
            return ""

    def get_value(self) -> str:
        """A method for getting the players in the team formatted for embed displaying

        :return: A formatted string with all player names on their own line
        :rtype: str
        """

        to_display_raw = self.data[:self.max_size] or self.data

        to_display_ready = [discord.utils.escape_markdown(player.display_name) for player in to_display_raw]

        if self.is_pickup and to_display_ready:
            to_display_ready[0] = f"**{to_display_ready[0]}**"

        return "\n".join(to_display_ready) or "_empty_"

    def blind_remove(self, player: discord.Member) -> bool:
        """A method for attempting to remove a player from the team without checking whether they exist first

        :param player: The player to attempt to remove
        :type player: discord.Member
        :return: Whether the operation was successful
        :rtype: bool
        """

        if player in self.data:
            self.data.remove(player)
            return True

        return False

    def is_full(self) -> bool:
        """A method to quickly check whether the team is full

        :return: A boolean result
        :rtype: bool
        """

        return self.max_size and len(self.data) >= self.max_size

    def set_voice_channel(self, voice_channel: discord.VoiceChannel):
        """A method for updating the voice channel associated with a team, useful

        :param voice_channel: The new voice channel should be associated with the team
        :type voice_channel: discord.VoiceChannel
        """

        self._voice_channel = voice_channel

    async def move_to_voice(self, *, success_required=True):
        """A method for attempting to move all players of the team into the team's voice channel

        kwargs
        ------

        :param success_required: Whether successfully moving all players should be required, default = True
        :type success_required: bool
        """

        if not self._voice_channel:
            if success_required:
                raise BotBaseInternalException("Required moving users into voice chat even without available voice "
                                               "channel.")
            else:
                return

        for player in self.data:
            try:
                await player.move_to(self._voice_channel, reason="ScrimBot: Setting up a scrim.")
            except discord.DiscordException:
                if success_required:
                    raise BotBaseUserException(f"Couldn't move user '{player.display_name}' "
                                               f"into channel '{self._voice_channel}'.", send_help=False)
