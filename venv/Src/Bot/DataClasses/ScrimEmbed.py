__version__ = "0.1"
__author__ = "Eetu Asikainen"

import discord

from Src.Bot.DataClasses.Game import Game
from Src.Bot.DataClasses.ScrimTeam import ScrimTeam
from Src.Bot.DataClasses.ScrimState import ScrimState

class ScrimEmbed(discord.Embed):
    def __init__(self, game: Game, is_ranked: bool, *, prefix=None, team_1_title="Team 1", team_2_title="Team 2"):
        super().__init__(title="Status", description= f"Looking for players. (0/{game.playercount})",
                         color = game.colour)

        self.set_author(name=f"{game.name} {'ranked ' if is_ranked else ''}scrim", icon_url=game.icon)

        self.add_field(name="**Players**", value="_empty_", inline=True)
        self.add_field(name="**Spectators**", value="_empty_", inline=True)
        self.set_footer(text=f"To join players react \U0001F3AE To join spectators react \U0001F441")

        self._state = ScrimState.LFP
        self._playerreq = game.playercount
        self._prefix = self._prefix or "/"

        # I am contenplating adding custom team names/custom teams in the future. These variables will save a lot of
        # time should I eventually do that
        self._team_1_title = team_1_title
        self._team_2_title = team_2_title

        # Even though storing player name string introduces duplicate data storage in the Scrim-ScrimEmbed -pair,
        # this streamlines the embed editing logic and simplifies the passed parameters needed
        self._participant_names = []
        self._spectator_names = []

        # Note that possible captains are not stored, 1st in the team list implies captain during pickup games
        self._team_1_names = []
        self._team_2_names = []

        # A helper list for displaying the picking order in pickup games
        self._picking_order = []


    def add_to_participants(self, user_name: str):
        self._participant_names.append(user_name)
        self._update_participant_fields()

    def remove_from_participants(self, user_name: str):
        self._participant_names.remove(user_name)
        self._update_participant_fields()

    def _update_participant_fields(self):
        self.set_field_at(0,
                          name=f"**Players** {'_(full)_' if len(self._participant_names) >= self._playerreq else ''}",
                          value="\n".join(self._participant_names[:self._playerreq]))

        if len(self._participant_names) > self._playerreq:

            self.description = \
                f"{self._playerreq} players present. Type '{self._prefix}lock' to lock the current players."

            if len(self.fields) < 3:
                self.add_field(name="**Player queue**", value="\n".join(self._participant_names[self._playerreq:]),
                               inline=True)
            else:
                self.set_field_at(2, name="**Player queue**",
                                  value="\n".join(self._participant_names[self._playerreq:]))

        else:
            self.description = \
                f"Looking for players. ({len(self._participant_names)}/{game.playercount})"

    def add_to_spectators(self, user_name: str):
        self._spectator_names.append(user_name)
        self.set_field_at(1, name="**Spectators**", value="\n".join(self._spectator_names))

    def remove_from_spectators(self, user_name: str):
        self._spectator_names.remove(user_name)
        self.set_field_at(1, name="**Spectators**", value="\n".join(self._spectator_names))


    def lock_scrim(self):
        self.description = \
            f"Players locked. Use reactions for manual team selection or type '**{self._prefix}teams**" + \
            "_random/balanced/balancedrandom/pickup_' to define teams automatically."

        self.set_field_at(0, "**Unassigned**", value="\n".join(self._participant_names[:self._playerreq]))

        div_string = "**------------------------------------------------------------**"
        if len(self.fields) < 3:
            self.add_field(current.embed.add_field(name=div_string, value=div_string, inline=False))

        else:
            self.set_field_at(2, name=div_string, value=div_string, inline=False)

        self.add_field(name=f"**{self._team_1_title}**", value="_empty_", inline=True)
        self.add_field(name=f"**{self._team_2_title}**", value="_empty_", inline=True)
        self.set_footer(text=f"React 1️⃣ to join {self._team_1_title} or 2️⃣ to join {self._team_2_title}.")


    def add_to_team_1(self, user_name: str):
        if user_name in self._team_2_names:
            self._team_2_names.remove(user_name)
        else:
            self._participant_names.remove(user_name)
        self._team_1_names.append(user_name)

        if self._state == ScrimState.CAPS and len(self._team_1_names) == 1:
            self._team_1_names[0] = "**" + self._team_1_names[0] + "**"

        self._update_teams_fields()

    def add_to_team_2(self, user_name: str):
        if user_name in self._team_1_names:
            self._team_1_names.remove(user_name)
        else:
            self._participant_names.remove(user_name)
        self._team_2_names.append(user_name)

        if self._state == ScrimState.CAPS and len(self._team_2_names) == 1:
            self._team_2_names[0] = "**" + self._team_2_names[0] + "**"

        self._update_teams_fields()

    def remove_from_team_1(self, user_name: str):

        # Special case for pickup games. Note that Scrim heavily curates the usage of these functions so error handling
        # is not necessary
        if self._state == ScrimState.CAPS and len(self._team_1_names) == 1:
            self._team_1_names = []

        else:
            self._team_1_names.remove(user_name)

        self._update_teams_fields()

    def remove_from_team_2(self, user_name: str):

        # Special case for pickup games. Note that Scrim heavily curates the usage of these functions so error handling
        # is not necessary
        if self._state == ScrimState.CAPS and len(self._team_2_names) == 1:
            self._team_2_names = []

        else:
            self._team_2_names.remove(user_name)

        self._update_teams_fields()

    def clear_teams(self):
        self._participant_names = self._participant_names + self._team_1_names + self._team_2_names
        self._team_1_names = []
        self._team_2_names = []

        self._update_teams_fields()

    def _update_teams_fields(self):
        self.set_field_at(0, "**Unassigned**", value="\n".join(self._participant_names) or "_empty_")
        self.set_field_at(
                3, name=f"**{self._team_1_title}** {'_full_' if len(self._team_1_names) >= self._playerreq/2 else ''}",
                value="\n".join(self._team_1_names) or "_empty_")
        self.set_field_at(
                4, name=f"**{self._team_2_title}** {'_full_' if len(self._team_2_names) >= self._playerreq / 2 else ''}",
                value="\n".join(self._team_2_names) or "_empty_")

        if not self._participant_names:
            self.description=f"The teams are ready. Write '{self._prefix}start' to start the scrim.";
            self.set_footer(text=f"Type '{self._prefix}teams clear' to clear teams")
        else:
            if self._state != ScrimState.CAPS:
                self.description = \
                    f"Players locked. Use reactions for manual team selection or type '**{self._prefix}teams**" + \
                    "_random/balanced/balancedrandom/pickup_' to define teams automatically."
            else:
                if self._team_1_names < 1 or self._team_2_names < 1:
                    self.description = "Setting up a pickup game. Waiting for players to choose captains. " + \
                                       f"{self._picking_order[0]} will start the drafting."
                    self.set_footer(text=f"React 1️⃣ to become captain of {self._team_1_title} " + \
                                         f"or 2️⃣ to become captain of {self._team_2_title}.")
                else:
                    self.description = f"Picking underway. Next to pick {self._picking_order.pop(0)}. " + \
                                       f"{len(self._participant_names)} players left to pick."
                    self.set_footer(text=f"Captains, user '**{self._prefix}pick** user' to pick players on your turn.")


    def start_scrim(self):
        self.remove_field(0)
        self.set_footer(text="Good luck, have fun! Declare the winner " + \
                             f"with '**{self._prefix}winner** _team1/team2/tie_")
        self.set_field_at(2, name=f"**{self._team_1_title}**", value="\n".join(self._team_1_names), inline=True)
        self.set_field_at(2, name=f"**{self._team_2_title}**", value="\n".join(self._team_2_names), inline=True)

    def declare_winner(self, winner: int):
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
        self.clear_fields()
        self.description = "Scrim terminated"
        self.set_footer(text=reason)

    def update_prefix(self, prefix: str):
        self._prefix = prefix
