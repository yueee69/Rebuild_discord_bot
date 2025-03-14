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

    def build_embed(self, user: nextcord.Member, custom_title) -> nextcord.Embed:
        item = self.item_manager.get_user(user.id)
        protect_status = get_protect_status_string(item.protect)

        embed = nextcord.Embed(
            title=custom_title,
            description=f'{user.mention} 以下是你的道具卡~',
            color=Toolkit.randomcolor()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="迴轉卡", value=item.trans_card, inline=False)
        embed.add_field(name="指定暱稱卡", value=item.nick_card, inline=False)
        embed.add_field(name="創建身分組卡", value=item.add_role_card, inline=False)
        embed.add_field(name="指定身分組卡", value=item.role_card, inline=False)
        embed.add_field(name="迴轉卡保護狀態", value=protect_status, inline=False)
        return embed


class Create:
    @staticmethod
    def get_components(interaction: Interaction, custom_title: str = "道具卡背包") -> BASIC_VIEW:
        embed = BackpackEmbedBuilder().build_embed(interaction.user, custom_title)
        return BASIC_VIEW.views(embed = embed, ephemeral = True)