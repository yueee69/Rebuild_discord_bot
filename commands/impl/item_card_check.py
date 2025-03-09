import nextcord
from nextcord import Interaction
import nextcord.ext.application_checks

from new_bot.commands.base_command import Cog_Extension
from views.item_crad_check_view import Create

class Item_card_check(Cog_Extension):
    def __init__(self, bot):
        super().__init__(bot)
        
    @nextcord.slash_command(name="道具卡背包", description="確認自己的道具卡數量")
    async def item_card_check(self, interaction: Interaction):  
        embed, view, ephemeral, content = Create.get_components(interaction)

        await interaction.response.send_message(
            ephemeral=ephemeral, 
            **({"embed": embed} if embed else {}),
            **({"view": view} if view else {}),
            **({"content": content} if content else {})
        )

def setup(bot):
    bot.add_cog(Item_card_check(bot))