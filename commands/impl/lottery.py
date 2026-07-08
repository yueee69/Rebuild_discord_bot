import nextcord
from nextcord import Interaction, SlashOption

from managers import user_manager
from views.lottery_views import get_components
from utils import global_views
from core import constants
from new_bot.commands.base_command import Cog_Extension

class Lottery(Cog_Extension):
    def __init__(self, bot):
        super().__init__(bot)
        
    @nextcord.slash_command(name="抽獎", description="展現陽壽的時候到了！", guild_ids=constants.ENABLE_COMMAND_USE_GUILDS)
    async def lottery(
        self,
        interaction: Interaction,
        pool:str = SlashOption(
            name = "選擇獎池",
            description="選擇你要的獎池",
            choices={
                "普通獎池": "norm_pool",
                "道具10連抽": "item_pool",
                #"王石獎池": "xtal_pool"
            },
            required=True
        )):
        user, status = user_manager.UserManager().get_user(interaction.user.id)
        components = global_views.UserCallback.get_Components(
            status,
            await get_components.lottery_views(pool, interaction, user)
        )

        if not interaction.response.is_done():
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
    bot.add_cog(Lottery(bot))
