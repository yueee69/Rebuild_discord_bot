import nextcord
from nextcord import Interaction

from new_bot.commands.base_command import Cog_Extension

from managers.history_manager import HistoryManager
from managers import user_manager
from utils import global_views
from core import constants

from views.lottery_history import Create

class Lottery_history(Cog_Extension):
    def __init__(self, bot):
        super().__init__(bot)

    @nextcord.slash_command(name='歷史紀錄', description='查看抽獎的歷史紀錄', guild_ids=constants.ENABLE_COMMAND_USE_GUILDS)
    async def lottery_history(
        self,
        interaction: Interaction, 
    ):
        userData = user_manager.UserManager()
        _, status = userData.get_user(interaction.user.id)
        
        historyData = HistoryManager().get_user(interaction.user.id)

        embed, view, ephemeral, content = global_views.UserCallback.get_Components(
            status, Create.get_components(historyData, interaction)
        )

        await interaction.response.send_message(
            ephemeral=ephemeral, 
            **({"embed": embed} if embed else {}),
            **({"view": view} if view else {}),
            **({"content": content} if content else {})
        )
        
def setup(bot):
    bot.add_cog(Lottery_history(bot))
