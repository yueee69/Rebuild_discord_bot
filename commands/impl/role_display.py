import nextcord
from nextcord import Interaction

from new_bot.commands.base_command import Cog_Extension

from callbacks.role_display_callback import Main_hindler

class Role_display(Cog_Extension):
    def __init__(self, bot):
        super().__init__(bot)
        
    @nextcord.slash_command(name="列出可被指定的身分組", description="展示可被操作的身分組")
    async def role_display(self, interaction: Interaction):
        await interaction.response.defer(with_message = True)

        embed, view, ephemeral, content = Main_hindler.main(interaction)
        await interaction.followup.send(
            ephemeral=ephemeral, 
            **({"embed": embed} if embed else {}),
            **({"view": view} if view else {}),
            **({"content": content} if content else {})
        )
      

def setup(bot):
    bot.add_cog(Role_display(bot))