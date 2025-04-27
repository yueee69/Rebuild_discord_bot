import nextcord

from utils.general import Toolkit

from views.BASIC_VIEW import BASIC_VIEW
from views.ERROR import Error

from views import nick_view
from views import create_role_view
from views import assign_role_view

from views.item_crad_check_view import Create

class ErrorHandler:
    @staticmethod
    def handle(StatusCode: object, due: str) -> BASIC_VIEW:
        if StatusCode.value != 0:
            return [Error.error(due = due)]
        return None


class Constructor:  
    def __init__(self, context: object):
        self.context = context
        self.BAG_ITEM_VIEW = Create.get_components(context.interaction, "以下是更新後的道具卡背包")

    def event_embed(self) -> BASIC_VIEW:
        embed = nextcord.Embed(
            title = "迴轉卡事件觸發！",
            description = self.context.event_message,
            color = Toolkit.randomcolor()
            )
        return BASIC_VIEW.views(embed = embed)

    def compelete(self) -> list[BASIC_VIEW]:
        maps = {
            "nick": nick_view.Create.result,
            "create_role": create_role_view.Create.result,
            "assign_role": assign_role_view.Create.result
        }
        result = []

        if self.context.event_message:
            result.append(self.event_embed())

        if not self.context.event_cancel:
            view = maps.get(self.context.service)(self.context)
            result.append(view)

        result.append(self.BAG_ITEM_VIEW)
        return result