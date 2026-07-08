#中介層，解耦用
from nextcord import Interaction

from dataclasses import dataclass

from callbacks import daily_shop_callback
from views import daily_shop_views, BASIC_VIEW
from utils.interaction_validator import InteractionValidator
from managers.daily_shop_manager import DailyShopManager, DailyShopData
from managers.user_manager import User, UserManager

from utils import global_views
from features.item_dumper import ItemRewardAllocator
from utils import Buytools

class Page:
    @staticmethod
    async def menu(interaction: Interaction):
        """
        第一次打開指令時機器人回復的主頁面
        """
        user, state = UserManager().get_user(interaction.user.id)
        comp = global_views.UserCallback.get_Components(
            state,
            Tool.get_main_page(interaction)
        )
        await daily_shop_callback.Message.send(interaction, comp) 

    @staticmethod
    async def go_to_menu(interaction: Interaction, before_interaction: Interaction):
        """
        按返回按紐時回到主頁面
        """
        if await InteractionValidator().check_authorization(before_interaction, interaction):
            comp = Tool.get_main_page(interaction)
            await daily_shop_callback.Message.edit(interaction, comp) 

    @staticmethod
    async def confirm_buy_goods(interaction: Interaction, before_interaction: Interaction):
        """
        編輯訊息，從主頁面跳到確認用戶購買商品
        """
        if await InteractionValidator().check_authorization(before_interaction, interaction):
            idx = int(interaction.data["custom_id"])
            item = Tool.get_item(idx)
            user = Tool.get_user(interaction.user.id)

            enough, button_name = Tool.get_button_info(user, item)
            context = ConfirmContext(
                user = user,
                item = item,
                index = idx,
                price = item.price,
                enough = enough,
                button_name = button_name,
                interaction = interaction
            )
            comp = Tool.get_buy_confirm_page(context)
            await daily_shop_callback.Message.edit(interaction, comp)

    @staticmethod
    async def confirm_yes(interaction: Interaction, before_interaction: Interaction, context: object):
        """
        用戶按了"購買"按鈕
        """
        if await InteractionValidator().check_authorization(before_interaction, interaction):
            """
            這裡再做一次判斷是為了用戶卡embed
            """
            shop_manager = DailyShopManager()
            item: DailyShopData = Tool.get_item(context.index)
            if shop_manager.user_has_purchased_today(interaction.user.id):
                comp = daily_shop_views.ConfirmYes(context).error_page("你今天已經購買過每日商店商品了，請明天再來。")
                await daily_shop_callback.Message.edit(interaction, comp)
                return

            if item.left_count <= 0: #沒了
                comp = daily_shop_views.ConfirmYes(context).error_page("此商品已賣完。")
                await daily_shop_callback.Message.edit(interaction, comp)
                return
            
            coin = Tool.get_user(context.interaction.user.id).coin
            if coin < item.price: #用戶的錢不夠
                comp = daily_shop_views.ConfirmYes(context).error_page(f"你的鮭魚幣不足，還缺 __**{item.price - coin}**__ 鮭魚幣")
                await daily_shop_callback.Message.edit(interaction, comp)
                return

            reserve_status = shop_manager.reserve_daily_purchase(interaction.user.id, context.index)
            if reserve_status == "already_purchased":
                comp = daily_shop_views.ConfirmYes(context).error_page("你今天已經購買過每日商店商品了，請明天再來。")
                await daily_shop_callback.Message.edit(interaction, comp)
                return
            if reserve_status == "sold_out":
                comp = daily_shop_views.ConfirmYes(context).error_page("此商品已賣完。")
                await daily_shop_callback.Message.edit(interaction, comp)
                return
            if reserve_status != "ok":
                comp = daily_shop_views.ConfirmYes(context).error_page("找不到這項商品，請重新開啟每日商店。")
                await daily_shop_callback.Message.edit(interaction, comp)
                return

            comp = daily_shop_views.ConfirmYes(context).get_page()
            Buytools.Calculater.daily_shop_buy(context, item.price)
            await daily_shop_callback.Message.edit(interaction, comp)
            await ItemRewardAllocator(
                items = [context.item.item],
                user_id = interaction.user.id,
                method = "買了",
                interaction = interaction
            ).apply()


@dataclass
class ConfirmContext:
    user: User
    item: DailyShopData
    index: int
    price: int
    enough: bool
    button_name: str
    interaction: Interaction

class Tool:
    @staticmethod
    def get_main_page(interaction: Interaction) -> BASIC_VIEW:
        """
        取得主頁面的page view
        """
        goods = DailyShopManager().get_goods()
        comp = daily_shop_views.MainPage(goods, interaction).get_page()
        return comp
    
    @staticmethod
    def get_buy_confirm_page(context: ConfirmContext):
        comp = daily_shop_views.ConfirmPage(context).get_page()
        return comp

    @staticmethod
    def get_user(user_id: int) -> User:
        user, _ = UserManager().get_user(user_id)
        return user

    @staticmethod
    def get_item(idx: int) -> DailyShopData:
        item = DailyShopManager().get_goods(idx)[0]
        return item
    
    @staticmethod
    def get_button_info(user: User, item: DailyShopData) -> str:
        enough = user.coin >= item.price
        button_name = "✅ 購買" if enough else f"還差 {(item.price - user.coin):,} 鮭魚幣"
        return enough, button_name
