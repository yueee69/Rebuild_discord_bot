import nextcord
from nextcord import Interaction

from new_bot.commands.base_command import Cog_Extension
from new_bot.core import constants

class Music_help(Cog_Extension):
    def __init__(self, bot):
        super().__init__(bot)
        
    @nextcord.slash_command(name="音樂指令幫助", description="顯示所有音樂指令的幫助")
    async def music_help(self, interaction: Interaction):  
        await interaction.response.send_message(content=constants.STR_MUSIC_HELP, ephemeral=True)

def setup(bot):
    bot.add_cog(Music_help(bot))