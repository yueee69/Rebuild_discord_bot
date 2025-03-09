import nextcord
from nextcord import Interaction

from new_bot.commands.base_command import Cog_Extension
from models import user_manager
from views.user_info_view import Create

class User_info(Cog_Extension):
    def __init__(self, bot):
        super().__init__(bot) 

    @nextcord.slash_command(name="用戶資訊", description="檢視你的各種資源")
    async def user_info(self, interaction: Interaction):
        user, status = user_manager.UserManager().get_user(interaction.user.id, from_register = True)
        embed, view, ephemeral, content = Create.get_components(interaction, user, status)

        await interaction.response.send_message(
            ephemeral=ephemeral, 
            **({"embed": embed} if embed else {}),
            **({"view": view} if view else {}),
            **({"content": content} if content else {})
        )

def setup(bot):
    bot.add_cog(User_info(bot))