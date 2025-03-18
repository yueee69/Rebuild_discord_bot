import nextcord
from nextcord import Interaction, SlashOption

from new_bot.commands.base_command import Cog_Extension

from callbacks.assogn_role_callback import Main_handler

class Assign_role(Cog_Extension):
    def __init__(self, bot):
        super().__init__(bot)

    @nextcord.slash_command(name='指定身分駔', description='指定身分組到某人身上')
    async def assign_role(
        self,
        interaction: Interaction, 
        user: nextcord.Member = SlashOption(name = "用戶", description = "選擇一個用戶！"),
        role: nextcord.Role = SlashOption(name = "身分組", description = "選擇一個身分組！")
        ):

        comp = await Main_handler.main(interaction, user, role, "assign_role")

        embed, view, ephemeral, content = comp[0]
        await interaction.response.send_message(
                ephemeral=ephemeral,
                **({"embed": embed} if embed else {}),
                **({"view": view} if view else {}),
                **({"content": content} if content else {})
            )


        for embed, view, ephemeral, content in comp[1:]:
            await interaction.followup.send(
                ephemeral=ephemeral,
                **({"embed": embed} if embed else {}),
                **({"view": view} if view else {}),
                **({"content": content} if content else {})
            )
        
def setup(bot):
    bot.add_cog(Assign_role(bot))