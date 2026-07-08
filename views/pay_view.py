from utils.general import Toolkit
from features.coin import coin_manager
from features.captcha import Captcha
from callbacks import pay_callback

from utils.interaction_validator import InteractionValidator
from utils.discord_model import GenericModal
from .BASIC_VIEW import BASIC_VIEW
from .ERROR import Error

import nextcord
from nextcord import Embed, Interaction, SelectOption, User, ButtonStyle, File
from nextcord.ui import View, Select, Button


class CkeckInputView:
    @staticmethod
    def need_input():
        return Error.error(
            due="請選擇一名成員，或輸入用戶名搜尋收款人。",
        )

    @staticmethod
    def input_not_found():
        return Error.error(
            due="找不到符合條件的已登記用戶，請換一個名稱再試一次。",
        )

    @staticmethod
    def select_user(user_data: list[User], old_interaction: Interaction):
        return BASIC_VIEW.views(
            embed=PayEmbeds.search_result(old_interaction, user_data),
            view=BuildView.from_user_select(user_data, old_interaction)
        )

    @staticmethod
    def main_page(interaction: Interaction, selected_user: User):
        return BASIC_VIEW.views(
            embed=PayEmbeds.main_page(interaction, selected_user),
            view=BuildView.build_coin_type_choice_button(selected_user, interaction)
        )


class InputPageView:
    @staticmethod
    def input_page(selected_user: User, coin_id: str, old_interaction: Interaction):
        coin_name = coin_manager.CoinManager(coin_id, old_interaction.user.id).get_coin_name()
        password_length = 4
        captcha = Captcha(password_length=password_length).generate_captcha()
        file = File(fp=captcha.image, filename="captcha.png")

        embed = PayEmbeds.input_page(
            old_interaction=old_interaction,
            selected_user=selected_user,
            coin_name=coin_name,
            password_length=password_length
        )
        embed.set_image(url="attachment://captcha.png")

        return BASIC_VIEW.views(
            embed=embed,
            file=file,
            view=BuildView.input_page_button(captcha.password, old_interaction, selected_user, coin_id)
        )

    @staticmethod
    def success_page(interaction: Interaction, selected_user: User, coin_name: str, amount: int, balance: int):
        return BASIC_VIEW.views(
            embed=PayEmbeds.success(interaction, selected_user, coin_name, amount, balance),
            clear_view=True
        )


class PayEmbeds:
    @staticmethod
    def main_page(interaction: Interaction, selected_user: User) -> Embed:
        embed = Embed(
            title="轉帳中心",
            description="確認收款人與可用餘額後，選擇要匯出的幣種。",
            color=Toolkit.randomcolor()
        )
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)

        coin_data = coin_manager.CoinManager("", interaction.user.id).get_all_coin_data()
        if coin_data:
            for coin_name, number in coin_data:
                value = f"`{number:,}`" if isinstance(number, int) else f"`{number}`"
                embed.add_field(name=coin_name, value=value, inline=True)
        else:
            embed.add_field(name="可用幣種", value="`目前沒有可轉帳的幣種`", inline=False)

        embed.add_field(
            name="收款人",
            value=f"{selected_user.mention}\n`{_display_user(selected_user)}`",
            inline=False
        )
        embed.set_footer(text="選擇幣種後會要求輸入金額與驗證碼。")
        return embed

    @staticmethod
    def search_result(interaction: Interaction, user_data: list[User]) -> Embed:
        embed = Embed(
            title="選擇收款人",
            description=f"找到 {len(user_data)} 名符合條件的已登記用戶。",
            color=Toolkit.randomcolor()
        )
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.set_footer(text="只能由發起轉帳的人操作此選單。")
        return embed

    @staticmethod
    def input_page(old_interaction: Interaction, selected_user: User, coin_name: str, password_length: int) -> Embed:
        embed = Embed(
            title="輸入轉帳資料",
            description="請確認收款人與幣種，接著按下按鈕輸入金額和驗證碼。",
            color=Toolkit.randomcolor()
        )
        embed.set_author(name=old_interaction.user.display_name, icon_url=old_interaction.user.display_avatar.url)
        embed.add_field(name="幣種", value=f"`{coin_name}`", inline=True)
        embed.add_field(name="金額", value="`尚未輸入`", inline=True)
        embed.add_field(
            name="收款人",
            value=f"{selected_user.mention}\n`{_display_user(selected_user)}`",
            inline=False
        )
        embed.set_footer(text=f"驗證碼共 {password_length} 碼，大小寫視為不同。")
        return embed

    @staticmethod
    def success(interaction: Interaction, selected_user: User, coin_name: str, amount: int, balance: int) -> Embed:
        embed = Embed(
            title="轉帳完成",
            description=f"{interaction.user.mention} 已成功轉帳給 {selected_user.mention}",
            color=nextcord.Colour.green()
        )
        embed.add_field(name="幣種", value=f"`{coin_name}`", inline=True)
        embed.add_field(name="金額", value=f"`{amount:,}`", inline=True)
        embed.add_field(name="你的餘額", value=f"`{balance:,}`", inline=True)
        embed.set_footer(text="交易已寫入資料庫。")
        return embed


class BuildView(View):
    def __init__(self, old_interaction: Interaction = None):
        super().__init__()
        self.old_interaction = old_interaction

    @classmethod
    def from_user_select(cls, user_data: list[User], old_interaction: Interaction) -> View:
        view = cls(old_interaction)
        options = [
            SelectOption(
                label=_display_user(user)[:100],
                description=user.name[:100],
                value=f"{user.id}"
            )
            for user in user_data
        ]
        select = Select(placeholder="選擇收款人", options=options)
        select.callback = view.from_user_select_callback
        view.add_item(select)
        return view

    async def from_user_select_callback(self, interaction: Interaction):
        if not await InteractionValidator.check_authorization(self.old_interaction, interaction):
            return
        await pay_callback.Callback(interaction).user_select_handle()

    @classmethod
    def build_coin_type_choice_button(cls, selected_user: User, old_interaction: Interaction) -> View:
        view = cls(old_interaction)
        button_info = coin_manager.CoinManager("", old_interaction.user.id).get_all_coin_button_info()
        for name, coin_id, available in button_info:
            button = Button(
                label=name,
                custom_id=f"pay_coin|{coin_id}|{selected_user.id}",
                disabled=not available,
                style=ButtonStyle.blurple
            )
            button.callback = view.coin_type_choice_callback
            view.add_item(button)
        return view

    async def coin_type_choice_callback(self, interaction: Interaction):
        if not await InteractionValidator.check_authorization(self.old_interaction, interaction):
            return
        await pay_callback.Callback(interaction).coin_type_choice_handle()

    @classmethod
    def input_page_button(cls, password: str, old_interaction: Interaction, selected_user: User, coin_id: str) -> View:
        view = cls(old_interaction)
        button = Button(
            label="輸入金額與驗證碼",
            custom_id=f"pay_submit|{password}|{selected_user.id}|{coin_id}",
            style=ButtonStyle.green
        )
        button.callback = view.input_page_button_callback
        view.add_item(button)
        return view

    async def input_page_button_callback(self, interaction: Interaction):
        if self.old_interaction.user.id != interaction.user.id and interaction.user.id not in InteractionValidator.ADMIN_ID:
            await InteractionValidator.send_error_response(interaction)
            return
        await pay_callback.Callback(interaction).send_input_data_modal()

    @classmethod
    def input_data_modal(cls, custom_id: str):
        return GenericModal(
            title="確認轉帳",
            input_fields=[
                {
                    "name": "amount",
                    "label": "轉帳金額",
                    "placeholder": "請輸入正整數",
                    "required": True,
                    "style": nextcord.TextInputStyle.short
                },
                {
                    "name": "password",
                    "label": "驗證碼",
                    "placeholder": "請輸入圖片中的驗證碼",
                    "required": True,
                    "style": nextcord.TextInputStyle.short
                }
            ],
            custom_callback=cls.on_submit,
            custom_id=custom_id
        )

    @staticmethod
    async def on_submit(interaction: Interaction, response: dict):
        amount = response["amount"]
        enter_password = response["password"]
        _, password, selected_user_id, coin_id = interaction.data["custom_id"].split("|", 3)
        await pay_callback.Callback(interaction).input_data_handle(
            amount,
            enter_password,
            password,
            selected_user_id,
            coin_id
        )


def _display_user(user: User) -> str:
    return getattr(user, "display_name", None) or getattr(user, "global_name", None) or user.name
