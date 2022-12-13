__version__ = "0.2"
__author__ = "Eetu Asikainen"

from hintedi import HinteDI

from Bot.DataClasses.Scrim import Scrim
from Bot.DataClasses.User import User


@HinteDI.singleton
class ScrimTeamOperationService:

    @staticmethod
    def add_to_team(scrim: Scrim, user: User, team_name: str):
        for team in [participant_team.team for participant_team in scrim.teams]:
            if team.name == team_name:
                team.members.append(user)

    @staticmethod
    def remove_from_team(scrim: Scrim, user: User):
        for team in [participant_team.team for participant_team in scrim.teams]:
            if user in team.members:
                team.members.remove(user)
