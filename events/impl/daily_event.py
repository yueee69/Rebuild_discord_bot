from managers.daily_shop_manager import DailyShopManager
from managers.item_manager import ItemManager
from managers.lottery_manager import LotteryStateManager
from managers.user_manager import UserManager


class DailyEvent:
    META_KEY = "daily_event_date"

    def __init__(
        self,
        user_manager: UserManager | None = None,
        daily_shop_manager: DailyShopManager | None = None,
        item_manager: ItemManager | None = None,
        lottery_manager: LotteryStateManager | None = None,
    ):
        self.user_manager = user_manager or UserManager()
        self.daily_shop_manager = daily_shop_manager or DailyShopManager()
        self.item_manager = item_manager or ItemManager()
        self.lottery_manager = lottery_manager or LotteryStateManager()

    async def run_if_needed(self) -> bool:
        today = UserManager.today_key()
        if self.user_manager.get_meta(self.META_KEY) == today:
            return False

        self.run_daily_events()
        self.user_manager.set_meta(self.META_KEY, today)
        return True

    def run_daily_events(self):
        self.user_manager.reset_daily_activity_if_needed()
        self.daily_shop_manager.daily_random_goods()
        self.item_manager.reset_daily_lottery_flags()
        self.lottery_manager.reset_daily_item_pool_flags()
