import nextcord
from nextcord import Interaction

from managers import user_manager
from new_bot.commands.base_command import Cog_Extension

from core import constants
from utils import global_views
from views.rank_view import Create

class Rank(Cog_Extension):
    def __init__(self, bot):
        super().__init__(bot)
        
    @nextcord.slash_command(name="排行榜", description="展示各種排行", guild_ids=constants.ENABLE_COMMAND_USE_GUILDS)
    async def rank(self, interaction: Interaction):
        userManager = user_manager.UserManager()
        _, status = userManager.get_user(interaction.user.id)

        embed, view, ephemeral, content = global_views.UserCallback.get_Components(
            status, Create.get_components()
        )
        await interaction.response.send_message(
            ephemeral=ephemeral, 
            **({"embed": embed} if embed else {}),
            **({"view": view} if view else {}),
            **({"content": content} if content else {})
        )
      

def setup(bot):
    bot.add_cog(Rank(bot))
