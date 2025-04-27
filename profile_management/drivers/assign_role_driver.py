from views.BASIC_VIEW import BASIC_VIEW

from profile_management.view_constructor import Constructor, ErrorHandler
from profile_management.resource_check import Assign_role_tool
from profile_management.card_events import event_handler
from profile_management.DiscordPermissionsTool.main_driver import DiscordTools

class Assign_role:
    @staticmethod
    async def driver(context: object) -> BASIC_VIEW:
        status, message = Assign_role_tool().check_resource(context)
        view = ErrorHandler.handle(status, message)
        if view:
            return view
        
        context.description = DiscordTools.generate_result_description(context)
        
        event_handler.Handler(context).main()
        if not context.event_cancel:
            context.created_role = await DiscordTools.assign_role(
                context.target_user,
                context.add_role,
                context.interaction.user,
                context.display_color
                )     

        Assign_role_tool().deduct_card(context)
        return Constructor(context).compelete()