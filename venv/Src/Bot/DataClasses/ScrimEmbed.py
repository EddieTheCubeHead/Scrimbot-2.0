__version__ = "0.1"
__author__ = "Eetu Asikainen"

from collections import OrderedDict

import discord

from Src.Bot.DataClasses.Game import Game
from Src.Bot.DataClasses.ScrimState import ScrimState
from Src.Bot.DataClasses.ScrimTeam import ScrimTeam

class ScrimEmbed(discord.Embed):
    """A subclass of discord.Embed that manages the embed part of the UI.

    methods
    -------

    update_participant_fields(participants, spectators)
        Update the embed according to the given ScrimTeam objects

    lock_scrim(unassigned, team_1, team_2)
        Update the embed to match the locked state of a scrim

    update_teams_fields(unassigned, team_1, team_2)
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

    def __init__(self, game: Game, is_ranked: bool, participants: ScrimTeam, spectators: ScrimTeam, *, prefix=None):
        """A constuctor for ScrimEmbed

        args
        ----

        :param game: The game the embed represents
        :type game: Game
        :param is_ranked: Whether the scrim is ranked
        :type is_ranked: bool
        :param participants: The participant ScrimTeam object of the scrim
        :type participants: ScrimTeam
        :param spectators: The spectator ScrimTeam object of the scrim
        :type spectators: ScrimTeam

        kwargs
        ------

        :param prefix: The server-specific prefix
        :type prefix: Optional[str]
        """

        super().__init__(title="Status", description= f"Looking for players. (0/{game.playercount})",
                         color = game.colour)

        self.set_author(name=f"{game.name} {'ranked ' if is_ranked else ''}scrim", icon_url=game.icon)

        self.add_field(name=participants.get_formatted_name(), value=participants.get_formatted_players(), inline=True)
        self.add_field(name=spectators.get_formatted_name(), value=spectators.get_formatted_players(), inline=True)
        self.set_footer(text=f"To join players react \U0001F3AE To join spectators react \U0001F441")

        self._state = ScrimState.LFP
        self._playerreq = game.playercount
        self._prefix = prefix or "/"

    def update_participant_fields(self, participants: ScrimTeam, spectators: ScrimTeam):
        """A method that takes ScrimTeam objects of participants and/or spectators and updates the embed accordingly

        args
        ----

        :param participants: All participants of the scrim
        :type participants: ScrimTeam
        :param spectators: All spectators of the scrim
        :type spectators: ScrimTeam
        """


        self.set_field_at(0, name=participants.get_formatted_name(), value=participants.get_formatted_players())

        queue_str = participants.get_formatted_queue()

        if participants.is_full():

            self.description = \
                f"{self._playerreq} players present. Type '{self._prefix}lock' to lock the current players."

            if queue_str:
                if len(self.fields) < 3:
                    self.add_field(name="**Player queue**", value=queue_str, inline=True)
                else:
                    self.set_field_at(2, name="**Player queue**", value=queue_str)

        else:

            self.description = \
                f"Looking for players. ({len(participants)}/{self._playerreq})"

            if not queue_str:
                if len(self.fields) >= 3:
                    self.remove_field(2)

        self.set_field_at(1, name=spectators.get_formatted_name(), value=spectators.get_formatted_players())

    def lock_scrim(self, unassigned: ScrimTeam, team_1: ScrimTeam, team_2: ScrimTeam):
        """A method for updating the embed to match a locked scrim and display required information

        :param unassigned: All unassigned players of the scrim
        :type unassigned: ScrimTeam
        :param team_1: Team 1 of the scrim
        :type team_1: ScrimTeam
        :param team_2: Team 2 of the scrim
        :type team_2: ScrimTeam
        """

        self.description = \
            f"Players locked. Use reactions for manual team selection or type '**{self._prefix}teams** " + \
            "_random/balanced/balancedrandom/pickup_' to define teams."

        self.set_field_at(0, name=unassigned.get_formatted_name(), value=unassigned.get_formatted_players())

        div_string = "------------------------------------------------------------"
        if len(self.fields) < 3:
            self.add_field(name=div_string, value=div_string, inline=False)

        else:
            self.set_field_at(2, name=div_string, value=div_string, inline=False)

        self.add_field(name="", value="", inline=True)
        self.add_field(name="", value="", inline=True)
        self.update_teams_fields(unassigned, team_1, team_2)

    def update_teams_fields(self, unassigned: ScrimTeam, team_1: ScrimTeam, team_2: ScrimTeam):
        """A private helper method for updating the displayed information based on the team dicts.

        :param unassigned: The unassigned players of the scrim
        :type unassigned: ScrimTeam
        :param team_1: Team 1 of the scrim
        :type team_1: ScrimTeam
        :param team_2: Team 2 of the scrim
        :type team_2: ScrimTeam
        """

        self.set_field_at(0, name=unassigned.get_formatted_name(), value=unassigned.get_formatted_players())
        self.set_field_at(3, name=team_1.get_formatted_name(), value=team_1.get_formatted_players())
        self.set_field_at(4, name=team_2.get_formatted_name(), value=team_2.get_formatted_players())

        if len(unassigned) == 0:
            self.description=f"The teams are ready. Write '{self._prefix}start' to start the scrim.";
            self.set_footer(text=f"Type '{self._prefix}teams clear' to clear teams")
        else:
            if self._state != ScrimState.CAPS:
                self.description = \
                    f"Players locked. Use reactions for manual team selection or type '**{self._prefix}teams** " + \
                    "_random/balanced/balancedrandom/pickup_' to define teams automatically."
                footertext = f"React 1️⃣ to join {team_1.get_formatted_name()} " + \
                             f"or 2️⃣ to join {team_2.get_formatted_name()}."
            else:
                if len(team_1) < 1 or len(team_2) < 1:
                    self.description = "Setting up a pickup game. Waiting for players to choose captains. " + \
                                       f"{self._picking_order[0]} will start the drafting."
                    footertext=f"React 1️⃣ to become captain of {team_1.get_formatted_name()} " + \
                               f"or 2️⃣ to become captain of {team_2.get_formatted_name()}."
                else:
                    self.description = f"Picking underway. Next to pick {self._picking_order.pop(0)}. " + \
                                       f"{len(unassigned)} players left to pick."
                    footertext=f"Captains, use '**{self._prefix}pick** user' to pick players on your turn."

                self.set_footer(text=footertext)

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

    def start_scrim(self, team_1: ScrimTeam, team_2: ScrimTeam):
        """A method for updating the embed to match a started scrim.

        :param team_1: Team 1 of the scrim
        :type team_1: ScrimTeam
        :param team_2: Team 2 of the scrim
        :type team_2: ScrimTeam
        """

        self.remove_field(0)
        self.description = "Scrim underway."
        self.set_footer(text="Good luck, have fun! Declare the winner " + \
                             f"with '{self._prefix}winner 1/2/tie'.")
        self.set_field_at(2, name=team_1.name, value=team_1.get_formatted_players())
        self.set_field_at(3, name=team_2.name, value=team_2.get_formatted_players())

    def declare_winner(self, winner: int):
        """A method for declaring a winner and updating the embed to display the final scrim state

        :param winner: The team that won given as a number. 0 means tie
        :type winner: int
        """

        if not winner:
            win_string = "Scrim over. It's a tie!"
        elif winner == 1:
            win_string = f"Scrim over. {self._team_1_title} won. Congratulations!"
        else:
            win_string = f"Scrim over. {self._team_2_title} won. Congratulations!"
        self.description = win_string
        self.set_footer(text="gg wp")
        self.remove_field(0)
        self.remove_field(0)


    def terminate(self, reason: str):
        """A method for updating the embed to match a terminated scrim and display the termination reason.

        :param reason: The reason for termination
        :type reason: str
        """

        self.clear_fields()
        self.description = "Scrim terminated"
        self.set_footer(text=reason)

    def update_prefix(self, prefix: str):
        """A method for updating the prefix displayed in the embed's command examples

        :param prefix: The new prefix of the guild the embed is on
        :type prefix: str
        """

        self._prefix = prefix
