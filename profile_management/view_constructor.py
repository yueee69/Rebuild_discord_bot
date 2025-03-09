from views import nick_view
from views.BASIC_VIEW import BASIC_VIEW
from views.ERROR import Error

class Constructor:
    @staticmethod
    def handle_error(StatusCode: object, due: str) -> BASIC_VIEW:
        if StatusCode.value != 0:
            return Error.error(due = due)
        
    @staticmethod
    def nick_complete(context: object) -> BASIC_VIEW:
        return nick_view.Create.result(context)