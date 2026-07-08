import nextcord
import nextcord.ext
from nextcord import Interaction
import nextcord.ext.application_checks

from managers.user_manager import UserManager
from utils import global_views
from core import constants

from new_bot.commands.base_command import Cog_Extension
from views.nick_view import Create

class Nick(Cog_Extension):
    def __init__(self, bot):
        super().__init__(bot)
        
    @nextcord.slash_command(name="指定暱稱", description="消耗卡片修改暱稱", guild_ids=constants.ENABLE_COMMAND_USE_GUILDS)
    @nextcord.ext.application_checks.guild_only() #只能在伺服器使用
    async def rank(
        self, 
        interaction: Interaction, 
        user: nextcord.Member = nextcord.SlashOption(name = '成員',description = "選擇一名要指定暱稱的成員")
    ):
        _, status = UserManager().get_user(interaction.user.id)
        components = global_views.UserCallback.get_Components(
            status,
            Create(user, "nick").get_components()
        )

        if isinstance(components, tuple):
                embed, view, ephemeral, content = components
                await interaction.response.send_message(
                ephemeral=ephemeral, 
                **({"embed": embed} if embed else {}),
                **({"view": view} if view else {}),
                **({"content": content} if content else {})
            )
        else:
            await interaction.response.send_modal(components)


def setup(bot):
    bot.add_cog(Nick(bot))
