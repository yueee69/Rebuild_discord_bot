from views.BASIC_VIEW import BASIC_VIEW

from profile_management.view_constructor import Constructor
from profile_management.resource_check import Assign_role_tool

from profile_management.DiscordPermissionsTool.main_driver import DiscordTools

class Assign_role:
    @staticmethod
    async def driver(context: object) -> BASIC_VIEW:
        status, message = Assign_role_tool().check_resource(context)
        view = Constructor.handle_error(status, message)
        if view:
            return view
        
        context.created_role = await DiscordTools.assign_role(
            context.target_user,
            context.add_role,
            context.interaction.user
            )
        Assign_role_tool().deduct_fortune(context)
        return Constructor.assign_role_complete(context)