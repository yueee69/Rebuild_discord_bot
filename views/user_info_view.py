from nextcord import Embed, Interaction
from nextcord.ui import View

from .BASIC_VIEW import BASIC_VIEW

class Create:
    @staticmethod
    def get_components(interaction: Interaction, user: object, status: str) -> tuple[Embed, View]:
        views = {
            "Found": Create.user_basic_info,
            "Notfound": Create.created_info
        }
        return views.get(status, lambda *_: BASIC_VIEW.views())(interaction, user)
    
    @staticmethod
    def user_basic_info(interaction: Interaction, user: object) -> tuple[Embed, View, bool]:
        embed = Embed(title=f"{interaction.user.display_name} 歡迎回來！", color=0xFFD700)
        embed.add_field(name="鮭魚幣", value=f'{user.coin:,}', inline=False)
        embed.add_field(name="陽壽", value=f'{user.fortune:,}', inline=False)
        embed.add_field(name="總共取得的鮭魚幣", value=f'{user.gain:,} | {user.gain/10000:.2f}萬', inline=False)
        embed.add_field(name="存活年數", value=f'{user.lvl:,}', inline=False)
        embed.add_field(name="今日講話取得的鮭魚幣", value=user.chat, inline=False)
        embed.add_field(name="今日通話取得的鮭魚幣", value=f'{user.voice} / 8000', inline=False)
        embed.add_field(name="今日直播取得的鮭魚幣", value=f'{user.stream} / 5000', inline=False)
        embed.add_field(name="今日購買的道具數量", value=f'{user.buy} / 1', inline=False)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        return BASIC_VIEW.views(embed = embed)

    @staticmethod
    def created_info(interaction: Interaction, user: object) -> tuple[Embed, View, bool]:
        embed = Embed(title="登記成功~", description=f"{interaction.user.mention}已完成登記！", color=0xFFD700)
        return BASIC_VIEW.views(embed = embed)
