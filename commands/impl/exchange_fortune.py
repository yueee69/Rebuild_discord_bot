import nextcord
from nextcord import Interaction, SlashOption

from new_bot.commands.base_command import Cog_Extension
from new_bot.views.exchnge_fortune_views import Create
from utils import global_views
from core import constants
from managers import user_manager

class Exchange_fortune(Cog_Extension):
    def __init__(self, bot):
        super().__init__(bot)

    @nextcord.slash_command(
        name='兌換陽壽',
        description=f'{constants.FORTUNE_COIN_PRICE}鮭魚幣=1陽壽',
        guild_ids=constants.ENABLE_COMMAND_USE_GUILDS
    )
    async def exchange_fortune(
        self,
        interaction: Interaction, 
        fortune:int = SlashOption(
            name="陽壽", 
            description="要兌換多少陽壽",
            min_value=1,
            required=True
        )):
        user, status = user_manager.UserManager().get_user(interaction.user.id)
        embed, view, ephemeral, content = global_views.UserCallback.get_Components(
            status, Create.check_user_status_components(fortune, user)
        )
        await interaction.response.send_message(
            ephemeral=ephemeral, 
            **({"embed": embed} if embed else {}),
            **({"view": view} if view else {}),
            **({"content": content} if content else {})
        )
        
def setup(bot):
    bot.add_cog(Exchange_fortune(bot))
