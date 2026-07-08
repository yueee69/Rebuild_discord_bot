from dataclasses import dataclass

import nextcord
import nextcord.ext
from nextcord import Interaction, SlashOption
import nextcord.ext.application_checks

from new_bot.commands.base_command import Cog_Extension

from core import constants
from managers.user_manager import UserManager
from utils import global_views

from callbacks import pay_callback

class Pay(Cog_Extension):
    def __init__(self, bot):
        super().__init__(bot)
        
    @nextcord.slash_command(name="匯款", description="將可轉帳的幣種匯給其他玩家", guild_ids=constants.ENABLE_COMMAND_USE_GUILDS)
    @nextcord.ext.application_checks.guild_only() #只能在伺服器使用
    async def pay(
        self, 
        interaction: Interaction,
        user: nextcord.Member = SlashOption(name = '成員',description = "（擇一）直接選擇收款成員", required = False),
        user_name: str = SlashOption(name = "用戶名", description="（擇一）輸入用戶名搜尋已登記用戶", required = False),
    ):
        input = UserInputData(interaction, user, user_name)

        _, status = UserManager().get_user(interaction.user.id)
        embed, view, ephemeral, content = global_views.UserCallback.get_Components(
            status,
            pay_callback.InputCheck(input).check()
        )
        
        await interaction.response.send_message(
            ephemeral=ephemeral, 
            **({"embed": embed} if embed else {}),
            **({"view": view} if view else {}),
            **({"content": content} if content else {})
        )


def setup(bot):
    bot.add_cog(Pay(bot))


@dataclass
class UserInputData:
    interaction: Interaction
    user: nextcord.Member
    user_name: str
    selected_user: nextcord.Member = None #先創一個空資料 後面給callback做更新
