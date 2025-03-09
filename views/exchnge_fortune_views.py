import nextcord
from nextcord.ui import Button, View
from nextcord import Embed, Interaction

from utils.general import Toolkit
from utils.Buytools import Calculater
from new_bot.callbacks import exchange_response_handler
from .BASIC_VIEW import BASIC_VIEW

class Create:
    @staticmethod
    def yes_or_no_button(user_object: object, fortune: int) -> View:
        confirm_button = Button(label="確認",custom_id="yes",style = nextcord.ButtonStyle.green)
        cancel_button = Button(label="取消",custom_id="no",style = nextcord.ButtonStyle.red)

        user = user_object.user

        callback = exchange_response_handler.ExchangeResponseHandler(user.user_id, user_object, fortune)
        
        confirm_button.callback = callback.on_check
        cancel_button.callback = callback.on_check
        view = View()
        view.add_item(confirm_button)
        view.add_item(cancel_button)

        return view 
    
    @staticmethod
    def check_user_status_components(fortune: int, user_object: object) -> tuple[Embed, View, bool]:

        user = user_object.user
        view = None

        if user.coin < fortune * 3500:
            embed = nextcord.Embed(title="捕捉到了一個小錯誤~")
            embed.add_field(name=f'• 鮭魚幣不足(缺少{ fortune * 3500 - user.coin }鮭魚幣)', value='',inline=False)
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
            embed.color = nextcord.Colour.red()
        
        elif fortune < 1:
            embed = nextcord.Embed(title="捕捉到了一個小錯誤~")
            embed.add_field(name="• 兌換的陽壽不能小於1", value='',inline=False)
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")
            embed.color = nextcord.Colour.red()

        else:
            view = Create.yes_or_no_button(user_object, fortune)
            embed = nextcord.Embed(title="付款確認", description=f"是否要消耗 {fortune*3500:,} 鮭魚幣兌換 {fortune} 陽壽?")
            embed.color = nextcord.Colour.dark_blue()
            
        return BASIC_VIEW.views(embed = embed, view = view)

    @staticmethod
    def exchange_user_callback(interaction: Interaction, buttonStatus: bool, fortune: int, user: object) -> tuple[Embed, View, bool]:

        callbacks = {
            "yes": Create.__exchange_success,
            "no": Create.__exchange_cancel
        }

        component = callbacks.get(buttonStatus, lambda *_: BASIC_VIEW.views())(interaction, fortune, user)
        return component

    @staticmethod
    def __exchange_success(interaction: Interaction,fortune: int, user: object):
        Calculater.exchange_fortune(user, fortune)
        return Create.__exchange_success_components(interaction, fortune, user)

    @staticmethod
    def __exchange_success_components(interaction: Interaction,fortune: int, user: object) -> tuple[Embed, View, bool]:
        embed = nextcord.Embed(title="你兌換成功啦！", color = nextcord.Colour.green())
        embed.add_field(name=f"{interaction.user.name}", value=f' 使用 {fortune * 3500:,} 鮭魚幣兌換了 {fortune} 陽壽',inline=True)
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/957718579887894558.webp")
        return BASIC_VIEW.views(embed = embed)
        
    @staticmethod
    def __exchange_cancel(interaction: Interaction, fortune: int, user: object) -> tuple[Embed, View, bool]:
        embed = nextcord.Embed(title="兌換取消", color = Toolkit.randomcolor())
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/928564939063455744.gif")
        return BASIC_VIEW.views(embed = embed)