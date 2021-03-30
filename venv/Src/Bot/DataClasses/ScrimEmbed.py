__version__ = "0.1"
__author__ = "Eetu Asikainen"

from collections import OrderedDict

import discord

from Src.Bot.DataClasses.Game import Game
from Src.Bot.DataClasses.ScrimState import ScrimState

class ScrimEmbed(discord.Embed):
    """A subclass of discord.Embed that manages the embed part of the UI.

    methods
    -------

    add_to_participants(user_id, user_name)
        Add an user to the participants in the embed

    remove_from_participants(user_id)
        Remove an user from the participants in the embed

    add_to_spectators(user_id, user_name)
        Add an user to the spectators in the embed

    remove_from_spectators(user_id)
        Remove and user from the spectators in the embed

    lock_scrim()
        Update the embed to match the locked state of a scrim

    add_to_team_1(user_id, user_name)
        Add an user to team 1 in the embed

    add_to_team_2(user_id, user_name)
        Add an user to team 2 in the embed

    remove_from_team(user_id)
        Remove a user from either team in the embed

    clear_teams()
        Remove all users from both teams in the embed

    start_scrim()
        Update the embed to match a started scrim

    declare_winner(winner)
        Update the embed to with winner information

    terminate(reason)
        Update the embed to represent a terminated scrim with a given termination reason

    update_prefix(prefix)
        Update the prefix shown on the embed command examples
    """

    def __init__(self, game: Game, is_ranked: bool, *, prefix=None, team_1_title="Team 1", team_2_title="Team 2"):
        """A constuctor for ScrimEmbed

        args
        ----

        :param game: The game the embed represents
        :type game: Game
        :param is_ranked: Whether the scrim is ranked
        :type is_ranked: bool

        kwargs
        ------

        :param prefix: The server-specific prefix
        :type prefix: Optional[str]
        :param team_1_title: A special
        :type team_1_title:
        :param team_2_title:
        :type team_2_title:
        """
        super().__init__(title="Status", description= f"Looking for players. (0/{game.playercount})",
                         color = game.colour)

        self.set_author(name=f"{game.name} {'ranked ' if is_ranked else ''}scrim", icon_url=game.icon)

        self.add_field(name="**Players**", value="_empty_", inline=True)
        self.add_field(name="**Spectators**", value="_empty_", inline=True)
        self.set_footer(text=f"To join players react \U0001F3AE To join spectators react \U0001F441")

        self._state = ScrimState.LFP
        self._playerreq = game.playercount
        self._prefix = prefix or "/"

        # I am contenplating adding custom team names/custom teams in the future. These variables will save a lot of
        # time should I eventually do that
        self._team_1_title = team_1_title
        self._team_2_title = team_2_title

        self._participant_names = OrderedDict()
        self._spectator_names = OrderedDict()

        # Note that possible captains are not stored, 1st in the team list implies captain during pickup games
        self._team_1_names = OrderedDict()
        self._team_2_names = OrderedDict()

        # A helper list for displaying the picking order in pickup games
        self._picking_order = []


    def add_to_participants(self, user_id: int, user_name: str):
        """A method for adding a user to the participants displayed in the embed

        args
        ----

        :param user_id: The unique discord id of the user
        :type user_id: int
        :param user_name: The name the user should be displayed with in the scrim
        :type user_name: str
        """
        self._participant_names[user_id] = user_name
        self._update_participant_fields()

    def remove_from_participants(self, user_id: int):
        """A method for removing a user from the participants displayed in the embed

        args
        ----

        :param user_id: The unique discord id of the user
        :type user_id: int
        """
        self._participant_names.pop(user_id)
        self._update_participant_fields()

    def _update_participant_fields(self):
        """A private helper method for updating the participant fields based on the participant dict."""
        self.set_field_at(0,
                          name=f"**Players** {'_(full)_' if len(self._participant_names) >= self._playerreq else ''}",
                          value="\n".join(list(self._participant_names.values())[:self._playerreq]) or "_empty_")

        if len(self._participant_names) >= self._playerreq:

            self.description = \
                f"{self._playerreq} players present. Type '{self._prefix}lock' to lock the current players."

        else:
            self.description = \
                f"Looking for players. ({len(self._participant_names)}/{self._playerreq})"

        if len(self._participant_names) > self._playerreq:

            if len(self.fields) < 3:
                self.add_field(name="**Player queue**",
                               value="\n".join(list(self._participant_names.values())[self._playerreq:]), inline=True)
            else:
                self.set_field_at(2, name="**Player queue**",
                                  value="\n".join(list(self._participant_names.values())[self._playerreq:]))

        else:
            if len(self.fields) >= 3:
                self.remove_field(2)

    def add_to_spectators(self, user_id: int, user_name: str):
        """A method for adding a user to the spectators in the embed

        args
        ----

        :param user_id: The unique discord id of the user
        :type user_id: int
        :param user_name: The name the user should be displayed with
        :type user_name: str
        """
        self._spectator_names[user_id] = user_name
        self.set_field_at(1, name="**Spectators**", value="\n".join(self._spectator_names.values()))

    def remove_from_spectators(self, user_id: int):
        """A method for removing a user from the spectators in the embed

        args
        ----

        :param user_id: The unique discord id of the user
        :type user_id: int
        """
        self._spectator_names.pop(user_id)
        self.set_field_at(1, name="**Spectators**", value="\n".join(self._spectator_names.values()) or "_empty_")


    def lock_scrim(self):
        """A method for updating the embed to match a locked scrim and display required information"""

        self.description = \
            f"Players locked. Use reactions for manual team selection or type '**{self._prefix}teams**" + \
            "_random/balanced/balancedrandom/pickup_' to define teams."

        while len(self._participant_names) > self._playerreq:
            self._participant_names.popitem()

        self.set_field_at(0, name="**Unassigned**", value="\n".join(self._participant_names.values()))

        div_string = "**------------------------------------------------------------**"
        if len(self.fields) < 3:
            self.add_field(name=div_string, value=div_string, inline=False)

        else:
            self.set_field_at(2, name=div_string, value=div_string, inline=False)

        self.add_field(name=f"**{self._team_1_title}**", value="_empty_", inline=True)
        self.add_field(name=f"**{self._team_2_title}**", value="_empty_", inline=True)
        self.set_footer(text=f"React 1️⃣ to join {self._team_1_title} or 2️⃣ to join {self._team_2_title}.")


    def add_to_team_1(self, user_id: int, user_name: str):
        """A method for adding a player into team 1

        args
        ----

        :param user_id: The unique discord id of the player
        :type user_id: int
        :param user_name: The name the player should be displayed with
        :type user_name: str
        """

        if user_id in self._team_2_names:
            self._team_2_names.pop(user_id)
        else:
            self._participant_names.pop(user_id)
        self._team_1_names[user_id] = user_name

        if self._state == ScrimState.CAPS and len(self._team_1_names) == 1:
            self._team_1_names[user_id] = "**" + user_name + "**"

        self._update_teams_fields()

    def add_to_team_2(self, user_id: int, user_name: str):
        """A method for adding a player into team 2

        args
        ----

        :param user_id: The unique discord id of the player
        :type user_id: int
        :param user_name: The name the player should be displayed with
        :type user_name: str
        """

        if user_name in self._team_1_names:
            self._team_1_names.pop(user_id)
        else:
            self._participant_names.pop(user_id)
        self._team_2_names[user_id] = user_name

        if self._state == ScrimState.CAPS and len(self._team_2_names) == 1:
            self._team_2_names[user_id] = "**" + user_name + "**"

        self._update_teams_fields()

    def remove_from_team(self, user_id: int):
        """A method for removing a player from their team

        args
        ----

        :param user_id: The unique discord id of the player
        :type user_id: int
        """

        self._team_1_names.pop(user_id, None)
        self._team_2_names.pop(user_id, None)
        self._update_teams_fields()

    def clear_teams(self):
        """A method for clearing both teams and assigning all players back to teamless players."""

        self._participant_names.update(self._team_1_names)
        self._participant_names.update(self._team_2_names)
        self._team_1_names = {}
        self._team_2_names = {}

        self._update_teams_fields()

    def _update_teams_fields(self):
        """A private helper method for updating the displayed information based on the team dicts."""

        self.set_field_at(0, "**Unassigned**", value="\n".join(self._participant_names.values()) or "_empty_")
        self.set_field_at(
                3, name=f"**{self._team_1_title}** {'_full_' if len(self._team_1_names) >= self._playerreq/2 else ''}",
                value="\n".join(self._team_1_names.values()) or "_empty_")
        self.set_field_at(
                4, name=f"**{self._team_2_title}** {'_full_' if len(self._team_2_names) >= self._playerreq / 2 else ''}",
                value="\n".join(self._team_2_names.values()) or "_empty_")

        if not self._participant_names:
            self.description=f"The teams are ready. Write '{self._prefix}start' to start the scrim.";
            self.set_footer(text=f"Type '{self._prefix}teams clear' to clear teams")
        else:
            if self._state != ScrimState.CAPS:
                self.description = \
                    f"Players locked. Use reactions for manual team selection or type '**{self._prefix}teams**" + \
                    "_random/balanced/balancedrandom/pickup_' to define teams automatically."
            else:
                if len(self._team_1_names) < 1 or len(self._team_2_names) < 1:
                    self.description = "Setting up a pickup game. Waiting for players to choose captains. " + \
                                       f"{self._picking_order[0]} will start the drafting."
                    self.set_footer(text=f"React 1️⃣ to become captain of {self._team_1_title} " + \
                                         f"or 2️⃣ to become captain of {self._team_2_title}.")
                else:
                    self.description = f"Picking underway. Next to pick {self._picking_order.pop(0)}. " + \
                                       f"{len(self._participant_names)} players left to pick."
                    self.set_footer(text=f"Captains, user '**{self._prefix}pick** user' to pick players on your turn.")


    def start_scrim(self):
        """A method for updating the embed to match a started scrim."""

        self.remove_field(0)
        self.set_footer(text="Good luck, have fun! Declare the winner " + \
                             f"with '**{self._prefix}winner** _team1/team2/tie_")
        self.set_field_at(2, name=f"**{self._team_1_title}**",
                          value="\n".join(self._team_1_names.values()), inline=True)
        self.set_field_at(2, name=f"**{self._team_2_title}**",
                          value="\n".join(self._team_2_names.values()), inline=True)

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
        """A method for updating the embed to match a terminated scrim and display the termination reason."""

        self.clear_fields()
        self.description = "Scrim terminated"
        self.set_footer(text=reason)

    def update_prefix(self, prefix: str):
        """A method for updating the prefix displayed in the embed's command examples

        :param prefix: The new prefix of the guild the embed is on
        :type prefix: str
        """

        self._prefix = prefix
