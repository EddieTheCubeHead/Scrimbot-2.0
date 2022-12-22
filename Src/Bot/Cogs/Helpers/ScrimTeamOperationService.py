__version__ = "0.2"
__author__ = "Eetu Asikainen"

from hintedi import HinteDI

from Src.Bot.DataClasses.ParticipantTeam import ParticipantTeam
from Src.Bot.DataClasses.Scrim import Scrim
from Src.Bot.DataClasses.Team import PARTICIPANTS, QUEUE, Team, SPECTATORS
from Src.Bot.DataClasses.User import User
from Src.Database.Core.MasterConnection import MasterConnection


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
    @HinteDI.inject
    def remove_from_team(scrim: Scrim, user: User, connection: MasterConnection):
        for participant_team in scrim.teams:
            team_member = next((member for member in participant_team.team.members if member.user_id == user.user_id),
                               None)
            if team_member is not None:
                participant_team.team.members.remove(team_member)
                if participant_team.team.name == PARTICIPANTS:
                    queue = next(search_team.team for search_team in scrim.teams if search_team.team.name == QUEUE)
                    while len(participant_team.team.members) < participant_team.max_size and queue.members:
                        participant_team.team.members.append(queue.members.pop(0))

    @staticmethod
    def clear_teams(scrim: Scrim):
        participants = next(team.team for team in scrim.teams if team.team.name == PARTICIPANTS)
        for team in [participant_team.team for participant_team in scrim.teams]:
            if team.name in (PARTICIPANTS, SPECTATORS, QUEUE):
                continue
            while team.members:
                participants.members.append(team.members.pop())
