import nextcord
from nextcord import Interaction

from .BASIC_VIEW import BASIC_VIEW
from utils.general import Toolkit
from managers.item_manager import ItemManager
from callbacks import change_card_protect_status

def get_protect_status_string(status: bool) -> str:
    return "🛡️ 開啟" if status else "關閉"

class BackpackEmbedBuilder:
    """
    負責建立使用者背包的 embed，
    將與背包內容相關的邏輯封裝於此。
    """
    def __init__(self):
        self.item_manager = ItemManager()

    def build_embed(self, user: nextcord.Member, custom_title: str, info_index: list[int]) -> nextcord.Embed:
        item = self.item_manager.get_user(user.id)
        protect_status = get_protect_status_string(item.protect)

        CARD_INFO = [
            ("迴轉卡", item.trans_card),
            ("指定暱稱卡", item.nick_card),
            ("創建身分組卡", item.add_role_card),
            ("指定身分組卡", item.role_card),
            ("迴轉卡保護狀態", protect_status)
        ]

        embed = nextcord.Embed(
            title=custom_title,
            description=f'{user.mention} 以下是你的道具卡~',
            color=Toolkit.randomcolor()
        )
        embed.set_thumbnail(url=user.display_avatar.url)

        for idx in sorted(info_index):
            name, value = CARD_INFO[idx]
            embed.add_field(name = name, value = value, inline = False)

        return embed

class ButtonBuilder:
    @staticmethod
    def build_button(name: str, style: nextcord.ButtonStyle, change_status: bool):
        button = nextcord.ui.Button(
            label = name,
            style = style,
            custom_id = str(change_status)
        )

        button.callback = change_card_protect_status.MainHandler().on_click
        return button

class ProtectButton:
    BUTTON_SETTING = [
        ("✅ 開啟保護", nextcord.ButtonStyle.green),
        ("❌ 關閉保護", nextcord.ButtonStyle.primary)
    ]

    def __init__(self):
        self.item_manager = ItemManager()
    
    def get_view(self, user_id: int | str):
        user_card_status = self.item_manager.get_user(user_id)
        index = int(user_card_status.protect)
        text, style = self.BUTTON_SETTING[index]

        button = ButtonBuilder.build_button(text, style, self.__get_reverse_status(user_card_status.protect))
        view = nextcord.ui.View()
        view.add_item(button)
        return view

    def __get_reverse_status(self, status: bool):
        return not status

class Create:
    @staticmethod
    def get_components(
        interaction: Interaction,
        custom_title: str = "道具卡背包", 
        info_index: list[int] = [0, 1 ,2 ,3, 4]
        ) -> BASIC_VIEW:
        """
        params:
            interacton: discord_interaction
            custom_title: 要指定的embed title
            info_index: 傳入對應卡片的index，用於只回覆某些卡片資訊 (0~4)
                迴轉卡: 0
                指定暱稱卡: 1
                創建身分組卡: 2
                指定身分組卡: 3
                迴轉卡保護狀態: 4
        """
        embed = BackpackEmbedBuilder().build_embed(interaction.user, custom_title, info_index)
        view = ProtectButton().get_view(interaction.user.id)
        return BASIC_VIEW.views(embed = embed, view = view, ephemeral = True)
