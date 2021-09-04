__version__ = "0.1"
__author__ = "Eetu Asikainen"

from typing import Optional, List

import discord

from Bot.DataClasses.Game import Game
from Bot.DataClasses.Team import Team
from Bot.DataClasses.ScrimState import ScrimState
from Bot.EmbedSystem.EmbedField import EmbedField


class ScrimEmbed(discord.Embed):
    """A subclass of discord.Embed that manages the embed part of the UI.

    methods
    -------

    update_participants(participants, spectators)
        Update the embed according to the given ScrimTeam objects

    lock_scrim(unassigned, team_1, team_2)
        Update the embed to match the locked state of a scrim

    update_teamss(unassigned, team_1, team_2)
        Update the embed according to the given ScrimTeam objects

    start_scrim()
        Update the embed to match a started scrim

    declare_winner(winner)
        Update the embed to with winner information

    terminate(reason)
        Update the embed to represent a terminated scrim with a given termination reason

    update_prefix(prefix)
        Update the prefix shown on the embed command examples
    """

    def __init__(self, game: Game, is_ranked: bool, participants: Team, spectators: Team, prefix=None):
        """A constuctor for ScrimEmbed

        args
        ----

        :param game: The game the embed represents
        :type game: Game
        :param is_ranked: Whether the scrim is ranked
        :type is_ranked: bool
        :param participants: The participant ScrimTeam object of the scrim
        :type participants: Team
        :param spectators: The spectator ScrimTeam object of the scrim
        :type spectators: Team

        kwargs
        ------

        :param prefix: The server-specific prefix
        :type prefix: Optional[str]
        """

        super().__init__(title="Status", description=f"Looking for players. {game.playercount} remaining.",
                         color=game.colour)

        self._picking_order: Optional[List[Team]] = None
        self.set_author(name=f"{game.name} {'ranked ' if is_ranked else ''}scrim", icon_url=game.icon)

        self.set_footer(text="To join players react \U0001F3AE To join spectators react \U0001F441")

        self._state: ScrimState = ScrimState.LFP
        self._playerreq: int = game.playercount
        self._prefix: str = prefix or "/"

        self._update_fields(participants, spectators)

    def _update_fields(self, *new_fields: EmbedField):
        """A private helper method that constructs the fields of the embed from a given list of EmbedField objects

        :param fields: The fields that should be displayed in the embed
        :type fields: list[EmbedField]
        """

        while len(self.fields) > len(new_fields):
            self.remove_field(0)

        for index, field in enumerate(new_fields):
            if index < len(self.fields):
                self.set_field_at(index, name=field.get_name(), value=field.get_value(), inline=field.inline)
            else:
                self.add_field(name=field.get_name(), value=field.get_value(), inline=field.inline)

    def update_participants(self, participants: Team, spectators: Team, queue: Team):
        """A method that takes ScrimTeam objects of participants and/or spectators and updates the embed accordingly

        args
        ----

        :param participants: All participants of the scrim
        :type participants: Team
        :param spectators: All spectators of the scrim
        :type spectators: Team
        :param queue: The queue of players who couldn't fit in the scrim. Can be empty, but not None
        :type queue: Team
        """

        if participants.is_full():

            description = f"{self._playerreq} players present. Type '{self._prefix}lock' to lock the current players."

        else:
            description = "Looking for players."

            if self._playerreq:
                description += f" {self._playerreq - len(participants)} remaining."

        self.description = description

        if queue:
            self._update_fields(participants, spectators, queue)

        else:
            self._update_fields(participants, spectators)

    def lock_scrim(self, unassigned: Team, spectators: Team, divider: EmbedField, team_1: Team,
                   team_2: Team):
        """A method for updating the embed to match a locked scrim and display required information

        args
        ----

        :param unassigned: All unassigned players of the scrim
        :type unassigned: Team
        :param spectators: The spectators of the scrim
        :type spectators: Team
        :param divider: A divider field between teamless participants and teams
        :type divider: EmbedField
        :param team_1: Team 1 of the scrim
        :type team_1: Team
        :param team_2: Team 2 of the scrim
        :type team_2: Team
        """

        self.description = \
            f"Players locked. Use reactions for manual team selection or type '**{self._prefix}teams** " + \
            "_random/balanced/balancedrandom/pickup_' to define teams."

        self.update_teams(unassigned, spectators, divider, team_1, team_2)

    def update_teams(self, unassigned: Team, spectators: Team, divider: EmbedField, team_1: Team,
                     team_2: Team):
        """A private helper method for updating the displayed information based on the team dicts

        args
        ----

        :param unassigned: The unassigned players of the scrim
        :type unassigned: Team
        :param spectators: The spectators of the scrim
        :type spectators: Team
        :param divider: A divider field between teamless participants and teams
        :type divider: EmbedField
        :param team_1: Team 1 of the scrim
        :type team_1: Team
        :param team_2: Team 2 of the scrim
        :type team_2: Team
        """

        if len(unassigned) == 0:
            self.description = f"The teams are ready. Write '{self._prefix}start' to start the scrim."
            self.set_footer(text=f"Type '{self._prefix}teams clear' to clear teams")
        else:
            if self._state != ScrimState.CAPS:
                self.description = \
                    f"Players locked. Use reactions for manual team selection or type '**{self._prefix}teams** " + \
                    "_random/balanced/balancedrandom/pickup_' to define teams automatically."
                footer_text = f"React 1️⃣ to join {team_1.get_name()} " + \
                              f"or 2️⃣ to join {team_2.get_name()}."
            else:
                if len(team_1) < 1 or len(team_2) < 1:
                    self.description = "Setting up a pickup game. Waiting for players to choose captains. " + \
                                       f"{self._picking_order[0]} will start the drafting."
                    footer_text = f"React 1️⃣ to become captain of {team_1.get_name()} " + \
                                  f"or 2️⃣ to become captain of {team_2.get_name()}."
                else:
                    self.description = f"Picking underway. Next to pick {self._picking_order.pop(0)}. " + \
                                       f"{len(unassigned)} players left to pick."
                    footer_text = f"Captains, use '**{self._prefix}pick** user' to pick players on your turn."

            self.set_footer(text=footer_text)

        self._update_fields(unassigned, spectators, divider, team_1, team_2)

    def wait_for_voice(self):
        """A method for updating the scrim's state to show waiting for players to join voice channels."""

        self.description = "Starting the scrim: waiting for all players to join voice channels."
        self.set_footer(text="Players, please join a voice channel to start the scrim.")

    def cancel_wait_for_voice(self):
        """A method for cancelling the waiting for voice state"""

        description_text = \
            f"Players locked. Use reactions for manual team selection or type '**{self._prefix}teams** " + \
            "_random/balanced/balancedrandom/pickup_' to define teams automatically."
        self.description = description_text
        self.set_footer(text=f"Type '{self._prefix}teams clear' to clear teams")

    def start_scrim(self, spectators: Team, divider: EmbedField, team_1: Team, team_2: Team):
        """A method for updating the embed to match a started scrim

        args
        ----

        :param spectators: The spectators of the scrim
        :type spectators: Team
        :param divider: A divider field between teamless participants and teams
        :type divider: EmbedField
        :param team_1: Team 1 of the scrim
        :type team_1: Team
        :param team_2: Team 2 of the scrim
        :type team_2: Team
        """

        self.description = "Scrim underway."
        self.set_footer(text="Good luck, have fun! Declare the winner "
                             f"with '{self._prefix}winner 1/2/tie'.")

        self._update_fields(spectators, divider, team_1, team_2)

    def declare_winner(self, team_1: Team, team_2: Team, winner: int):
        """A method for declaring a winner and updating the embed to display the final scrim state

        args
        ----

        :param team_1: Team 1 of the scrim
        :type team_1: Team
        :param team_2: Team 2 of the scrim
        :type team_2: Team
        :param winner: The team that won given as a number. 0 means tie
        :type winner: int
        """

        if winner == 0:
            win_string = "Scrim over. It's a tie!"
        else:
            win_string = f"Scrim over. {team_1.name if winner == 1 else team_2.name} won. Congratulations!"
        self.description = win_string
        self.set_footer(text="gg wp")

        self._update_fields(team_1, team_2)

    def terminate(self, reason: str):
        """A method for updating the embed to match a terminated scrim and display the termination reason

        args
        ----

        :param reason: The reason for termination
        :type reason: str
        """

        self.clear_fields()
        self.description = "Scrim terminated"
        self.set_footer(text=reason)

    def update_prefix(self, prefix: str):
        """A method for updating the prefix displayed in the embed's command examples

        args
        ----

        :param prefix: The new prefix of the guild the embed is on
        :type prefix: str
        """

        self._prefix = prefix
