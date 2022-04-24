__version__ = "0.2"
__author__ = "Eetu Asikainen"

import os

from Bot.EmbedSystem.ScrimStates.StartedState import StartedState
from Utils.TestBases.StateUnittest import StateUnittest


class TestStartedState(StateUnittest):

    def test_build_description_given_game_has_two_teams_then_winner_and_tie_instructions_returned(self):
        state = StartedState()
        self.assertEqual("Test scrim underway. Declare the winner with the command 'winner [team]' or 'tie' or end the "
                         "scrim without declaring a winner with 'end'.",
                         state.build_description(self.teams_manager))

    def test_build_description_given_game_has_more_than_two_teams_then_winner_instructions_returned_with_no_tie(self):
        state = StartedState()
        self.teams_manager.game = self.create_mock_game("Test", 3, 5)
        self.assertEqual("Test scrim underway. Declare the winner with the command 'winner [team]' or end the scrim "
                         "without declaring a winner with 'end'.",
                         state.build_description(self.teams_manager))

    def test_build_description_given_ffa_game_with_two_players_then_user_winner_and_tie_instructions_returned(self):
        state = StartedState()
        self.teams_manager.game = self.create_mock_game("Test", 1, 2)
        self.assertEqual("Test scrim underway. Declare the winner with the command 'winner [user]' or 'tie' or end the "
                         "scrim without declaring a winner with 'end'.",
                         state.build_description(self.teams_manager))

    def test_build_description_given_ffa_game_with_three_or_more_players_then_user_winner_instructions_returned(self):
        state = StartedState()
        self.teams_manager.game = self.create_mock_game("Test", 1, 3)
        self.assertEqual("Test scrim underway. Declare the winner with the command 'winner [user]' or end the scrim "
                         "without declaring a winner with 'end'.",
                         state.build_description(self.teams_manager))

    def test_build_fields_when_called_then_returns_only_team_fields(self):
        self.add_team_1(*list(range(5)))
        self.add_team_2(*list(range(5, 9)))
        state = StartedState()
        expected_team_1 = "<@" + f">{os.linesep}<@".join([str(num) for num in range(5)]) + ">"
        expected_team_2 = "<@" + f">{os.linesep}<@".join([str(num) for num in range(5, 9)]) + ">"
        actual_fields = state.build_fields(self.teams_manager)
        self.assertEqual([("Team 1", expected_team_1, True),
                          ("Team 2", expected_team_2, True)], actual_fields)

    def test_build_footer_when_called_then_returns_gl_hf(self):
        state = StartedState()
        self.assertEqual("gl hf!", state.build_footer(self.teams_manager))
