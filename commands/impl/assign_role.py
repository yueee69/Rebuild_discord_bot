import nextcord
import nextcord.ext.application_checks
from nextcord import Interaction, SlashOption

from new_bot.commands.base_command import Cog_Extension

from core import constants
from managers.user_manager import UserManager
from utils import global_views
from new_bot.callbacks import assign_role_callback

class Assign_role(Cog_Extension):
    def __init__(self, bot):
        super().__init__(bot)

    @nextcord.slash_command(name='指定身分組', description='指定身分組到某人身上', guild_ids=constants.ENABLE_COMMAND_USE_GUILDS)
    @nextcord.ext.application_checks.guild_only()
    async def assign_role(
        self,
        interaction: Interaction, 
        user: nextcord.Member = SlashOption(name = "用戶", description = "選擇一個用戶！"),
        role: nextcord.Role = SlashOption(name = "身分組", description = "選擇一個身分組！")
        ):

        data = assign_role_callback.State_manager(
            target = user, 
            role = role, 
            service = "assign_role", 
            interaction = interaction
            )
        
        _, status = UserManager().get_user(interaction.user.id)
        embed, view, ephemeral, content = global_views.UserCallback.get_Components(
            status,
            await assign_role_callback.SelectHandler().get_components(data)
        )

        await interaction.response.send_message(
                ephemeral=ephemeral,
                **({"embed": embed} if embed else {}),
                **({"view": view} if view else {}),
                **({"content": content} if content else {})
            )

        
def setup(bot):
    bot.add_cog(Assign_role(bot))
