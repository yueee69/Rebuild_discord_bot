import nextcord
from nextcord import Interaction

from .BASIC_VIEW import BASIC_VIEW
from utils.general import Toolkit
from models.item_manager import ItemManager


def get_protect_status_string(status: bool) -> str:
    return "開啟" if status else "關閉"

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
        return BASIC_VIEW.views(embed = embed, ephemeral = True)