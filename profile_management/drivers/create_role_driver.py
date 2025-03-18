from views.BASIC_VIEW import BASIC_VIEW

from profile_management.view_constructor import Constructor, ErrorHandler
from profile_management.resource_check import Create_role_tool

from profile_management.DiscordPermissionsTool.main_driver import DiscordTools

class Create_role:
    @staticmethod
    async def driver(context: object) -> BASIC_VIEW:
        status, message = Create_role_tool().check_resource(context)
        view = ErrorHandler.handle(status, message)
        if view:
            return view
        
        context.created_role = await DiscordTools.create_role(
            context.interaction.guild, 
            context.create_role_name, 
            context.create_role_color, 
            context.interaction.user
            )
        Create_role_tool().deduct_fortune(context)
        return Constructor(context).compelete()
        
    