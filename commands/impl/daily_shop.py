import nextcord
from nextcord import Interaction

from command_factory import daily_shop_factory

from new_bot.commands.base_command import Cog_Extension
from core import constants

class DailyShop(Cog_Extension):
    def __init__(self, bot):
        super().__init__(bot)

    @nextcord.slash_command(name='每日商店', description='查看今天的每日商店，選購限時商品！', guild_ids=constants.ENABLE_COMMAND_USE_GUILDS)
    async def daily_shop(
        self,
        interaction: Interaction
    ):
        await daily_shop_factory.Page.menu(interaction)
        

def setup(bot):
    bot.add_cog(DailyShop(bot))
