__version__ = "0.2"
__author__ = "Eetu Asikainen"

from hintedi import HinteDI

from Bot.DataClasses.ParticipantTeam import ParticipantTeam
from Bot.DataClasses.Scrim import Scrim
from Bot.DataClasses.Team import PARTICIPANTS, QUEUE, Team
from Bot.DataClasses.User import User


def _handle_add_to_team(participant_team: ParticipantTeam, user: User, team_name: str) -> str:
    if participant_team.team.name == PARTICIPANTS:
        if participant_team.max_size != 0 and len(participant_team.team.members) >= participant_team.max_size:
            return QUEUE
    participant_team.team.members.append(user)
    return team_name


@HinteDI.singleton
class ScrimTeamOperationService:

    @staticmethod
    def add_to_team(scrim: Scrim, user: User, team_name: str):
        for participant_team in scrim.teams:
            if participant_team.team.name == team_name:
                team_name = _handle_add_to_team(participant_team, user, team_name)

    @staticmethod
    def remove_from_team(scrim: Scrim, user: User):
        for participant_team in scrim.teams:
            if user in participant_team.team.members:
                participant_team.team.members.remove(user)
                if participant_team.team.name == PARTICIPANTS:
                    queue = next(search_team.team for search_team in scrim.teams if search_team.team.name == QUEUE)
                    while len(participant_team.team.members) < participant_team.max_size and queue.members:
                        participant_team.team.members.append(queue.members.pop(0))

