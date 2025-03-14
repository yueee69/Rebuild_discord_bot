import nextcord
import nextcord.ext
from nextcord import Interaction
import nextcord.ext.application_checks

from new_bot.commands.base_command import Cog_Extension
from callbacks import create_role_callback

class Create_role(Cog_Extension):
    def __init__(self, bot):
        super().__init__(bot)
        
    @nextcord.slash_command(name="創建身分組", description="消耗卡片創建身分組")
    @nextcord.ext.application_checks.guild_only() #只能在伺服器使用
    async def create_role(
        self, 
        interaction: Interaction, 
    ):
        embed, view, ephemeral, content = await create_role_callback.SelectHandler("create_role").get_components()
        await interaction.response.send_message(
            ephemeral=ephemeral, 
            **({"embed": embed} if embed else {}),
            **({"view": view} if view else {}),
            **({"content": content} if content else {})
        )

def setup(bot):
    bot.add_cog(Create_role(bot))