import nextcord
from nextcord.ui import View, Button
from nextcord import Embed, Interaction

from utils.general import Toolkit
from .BASIC_VIEW import BASIC_VIEW
from .ERROR import Error
from command_factory import daily_shop_factory
from models.daily_shop_manager import DailyShopData

class MainPage:
    def __init__(self, goods: list[DailyShopData], interaction: Interaction):
        self.goods = goods 
        self.interaction = interaction
        self.user = interaction.user

    def get_page(self) -> BASIC_VIEW:
        return BASIC_VIEW.views(
            embed = self.build_shop_main_embed(),
            view = MainShopView(self.interaction, self.goods)
            )

    def build_shop_main_embed(self) -> Embed:
        time = Toolkit.get_time()
        embed = Embed(
            title = f" ─ {Toolkit.get_greeting()}！{self.user.display_name}，今天是 `{time.month}/{time.day}`",    
            color = Toolkit.randomcolor()
        )
        embed.set_author(name = "商品清單（每日凌晨刷新）", icon_url = self.user.display_avatar.url)

        for idx, item in enumerate(self.goods, start = 1):
            separator = "\n╍╍╍╍╍╍╍╍╍╍╍╍" if idx < len(self.goods) else ""
            embed.add_field(
                name = f"商品：{item.item}",
                value = f"價格：**{item.price:,}**\n剩餘數量：**{self.__get_count(item.left_count)}**{separator}",
                inline = False
            )
        return embed
    
    def __get_count(self, count: int):
        return "今日已售完！" if count == 0 else count
    
    
class ConfirmPage:
    def __init__(self, context: object):
        self.context = context
        self.has_enough = context.enough
        self.item = context.item
        self.interaction = context.interaction
        self.user = context.interaction.user
        self.button_name = context.button_name

    def get_page(self) -> BASIC_VIEW:
        return BASIC_VIEW.views(
            embed = self.build_confirm_embed(),
            view = ConfirmBuyView(self.context)
        )
    
    def build_confirm_embed(self) -> Embed:
        embed = Embed(
            title = "是否購買這個商品？",
            description = f"**商品：{self.item.item}**\n價格：**{self.item.price:,}**\n剩餘數量：**{self.item.left_count}**",
            color = Toolkit.randomcolor()
        )
        embed.set_author(name = "商品清單（每日凌晨刷新）", icon_url = self.user.display_avatar.url)

        return embed
    

class ConfirmYes:
    def __init__(self, context: object):
        self.context = context
        self.item = context.item
        self.interaction = context.interaction
        self.user = context.interaction.user

    def get_page(self) -> BASIC_VIEW:
        return BASIC_VIEW.views(
            embed = self.build_confirm_embed(),
            clear_view = True
        )
    
    def error_page(self, due: str) -> BASIC_VIEW:
        return Error.error(
            due = due,
            view = ConfirmBuyView(self.context, disable_buy_button = True)
        )

    def build_confirm_embed(self):
        embed = Embed(
            title = "購買成功！",
            description = f"**商品：{self.item.item}**\n價格：**{self.item.price:,}**",
            color = Toolkit.randomcolor(),
        )
        embed.set_author(name = "商品清單（每日凌晨刷新）", icon_url = self.user.display_avatar.url)
        embed.set_thumbnail(url = "https://cdn.discordapp.com/emojis/1075897670029287455.gif")

        return embed


class MainShopView(View):
    def __init__(self, interaction: Interaction, goods: list[DailyShopData]):
        super().__init__()
        self.interaction = interaction
        self.goods = goods

        for idx, item in enumerate(goods):
            button = Button(
                label = f"購買 {item.item}",
                custom_id = f"{idx}",
                style = nextcord.ButtonStyle.blurple,
                disabled = not bool(item.left_count)
            )
            button.callback = self.callback
            self.add_item(button)

    async def callback(self, interaction: Interaction):
        await daily_shop_factory.Page.confirm_buy_goods(interaction, self.interaction)

class ConfirmBuyView(View):
    def __init__(self, context: object, disable_buy_button: bool = False):
        self.context = context
        self.interaction = context.interaction
        self.user_has_enough = context.enough
        self.button_label = context.button_name

        super().__init__()
        self.build_cancel_button()
        if not disable_buy_button:
            self.build_buy_button()

    def build_cancel_button(self):
        self.cancel_button = Button(label="⮌ 返回", style = nextcord.ButtonStyle.red)
        self.cancel_button.callback = self.on_cancel
        self.add_item(self.cancel_button)

    def build_buy_button(self):
        buy_button_style = nextcord.ButtonStyle.green if self.user_has_enough else nextcord.ButtonStyle.blurple
        self.buy_button = Button(label = self.button_label, style = buy_button_style, disabled = not self.user_has_enough)
        self.buy_button.callback = self.on_confirm
        self.add_item(self.buy_button)  

    async def on_confirm(self, interaction: Interaction):
        await daily_shop_factory.Page.confirm_yes(interaction, self.interaction, self.context)

    async def on_cancel(self, interaction: Interaction):
        await daily_shop_factory.Page.go_to_menu(interaction, self.interaction)

