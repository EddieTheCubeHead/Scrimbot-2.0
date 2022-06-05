__version__ = "0.1"
__author__ = "Eetu Asikainen"


from Bot.Checks.CheckBase import CheckBase
from Bot.Core.ScrimContext import ScrimContext
from Bot.DataClasses.GuildMember import PermissionLevel
from Bot.Exceptions.BotInvalidPermissionsException import BotInvalidPermissionsException


class PermissionsCheck(CheckBase):

    def __init__(self, permission_level: PermissionLevel):
        self._permission_level = permission_level

    async def check(self, ctx: ScrimContext):
        max_permission_level = PermissionLevel.member
        if ctx.author.guild_permissions.administrator:
            max_permission_level = PermissionLevel.admin
        if max_permission_level >= self._permission_level:
            return True
        raise BotInvalidPermissionsException(ctx, self._permission_level, max_permission_level)
