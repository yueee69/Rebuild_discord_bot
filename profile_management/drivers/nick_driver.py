from views.BASIC_VIEW import BASIC_VIEW

from profile_management.view_constructor import Constructor
from profile_management.resource_check import NickTool

from profile_management.DiscordPermissionsTool.main_driver import DiscordTools

class Nick:
    #這裡會是各種工具的集合 但不會有邏輯的實現 只有調用
    @staticmethod
    async def driver(context: object) -> BASIC_VIEW:
        status, message = NickTool().check_resource(context)
        view = Constructor.handle_error(status, message)
        if view:
            return view
        
        await DiscordTools.nick(context.target_user, context.nick_name)
        NickTool().deduct_fortune(context)
        return Constructor.nick_complete(context)
        
    