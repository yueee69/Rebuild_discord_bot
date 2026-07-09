from Lottery import dump_items
from Lottery import gacha_resource
from Lottery import gacha_tools
from Lottery import view_constructor

from core import constants
from managers.lottery_manager import LotteryStateManager

class Driver:
    """
    流程: 檢查 -> 有錯就return view -> 抽獎(如果沒錯) -> dump獎品 -> return view
    """
    @staticmethod
    def norm_pool(userData: object, times: int):
        pool = gacha_resource.NormPool()
        status, message, times = pool.check_resource(userData, times)

        view = view_constructor.Constructor.handle_error(status, message)
        if view:
            return view

        userLotteryData = LotteryStateManager().get(userData.user_id)

        prize = gacha_tools.Norm_pool().draw(userLotteryData, times)
        dump_items.Norm_pool().dump_items(prize, userData)
        pool.deduct_fortune(userData, times)

        return view_constructor.Constructor.compelete(prize)
    
    @staticmethod
    def item_pool(userData: object, times: int):
        pool = gacha_resource.ItemPool()
        userLotteryData = LotteryStateManager().get(userData.user_id)
        status, message = pool.check_resource(userData, times, userLotteryData)

        view = view_constructor.Constructor.handle_error(status, message)
        if view:
            return view

        userLotteryData.item_pool_is_lottery = True

        prize = gacha_tools.Item_pool().draw(constants.ITEM_LOTTERY_DRAW_COUNT)
        dump_items.Item_pool().dump_items(prize, userData)
        pool.deduct_fortune(userData, 1)

        return view_constructor.Constructor.item_compelete(prize)
    
    @staticmethod
    def xtal_pool(userData: object, times: int):
        return
        #比較複雜 先搞定其他
