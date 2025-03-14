from views.BASIC_VIEW import BASIC_VIEW
from views.ERROR import Error

from views import nick_view
from views import create_role_view

from views.item_crad_check_view import Create

class Constructor:
    @staticmethod
    def handle_error(StatusCode: object, due: str) -> BASIC_VIEW:
        if StatusCode.value != 0:
            return Error.error(due = due)
        
    @staticmethod
    def nick_complete(context: object) -> BASIC_VIEW:
        return trans_to_list_and_add_card_check(nick_view.Create.result(context), context)
    
    @staticmethod
    def create_role_complete(context: object) -> BASIC_VIEW:
        return trans_to_list_and_add_card_check(create_role_view.Create.result(context), context)
    
def trans_to_list_and_add_card_check(original_view: BASIC_VIEW, context: object):
    return [original_view, Create.get_components(context.interaction, "以下是更新後的道具卡背包")]