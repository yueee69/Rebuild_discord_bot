from views import lottery_views
from views.BASIC_VIEW import BASIC_VIEW

from views.ERROR import Error

class Constructor:
    @staticmethod
    def handle_error(StatusCode: object, due: str):
        if StatusCode.value != 0:
            return Error.error(due)
        
    @staticmethod
    def compelete(prizes: list) -> BASIC_VIEW:
        return lottery_views.Result.result(prizes)
    
    @staticmethod
    def item_compelete(prizes: list) -> BASIC_VIEW:
        return lottery_views.Item_pool_components.result(prizes)
    