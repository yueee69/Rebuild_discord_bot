import nextcord
from nextcord import Interaction, SlashOption

from new_bot.commands.base_command import Cog_Extension
from new_bot.views.exchnge_fortune_views import Create
from utils import global_views
from models import user_manager

class Exchange_fortune(Cog_Extension):
    def __init__(self, bot):
        super().__init__(bot)

    @nextcord.slash_command(name='兌換陽壽', description='3500鮭魚幣=1陽壽')
    async def exchange_fortune(
        self,
        interaction: Interaction, 
        fortune:int = SlashOption(
            name="陽壽", 
            description="要兌換多少陽壽",
            required=True
        )):
        userData = user_manager.UserManager()
        _, status = userData.get_user(interaction.user.id)
        embed, view, ephemeral, content = global_views.UserCallback.get_Components(
            status, Create.check_user_status_components(fortune, userData)
        )
        await interaction.response.send_message(
            ephemeral=ephemeral, 
            **({"embed": embed} if embed else {}),
            **({"view": view} if view else {}),
            **({"content": content} if content else {})
        )
        
def setup(bot):
    bot.add_cog(Exchange_fortune(bot))