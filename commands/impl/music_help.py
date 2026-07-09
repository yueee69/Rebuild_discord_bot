import nextcord
from nextcord import Interaction
from nextcord.ext import application_checks

from new_bot.commands.base_command import Cog_Extension
from new_bot.core import constants
from views.music_views import MusicHelpPage, component_kwargs


class Music_help(Cog_Extension):
    def __init__(self, bot):
        super().__init__(bot)

    @nextcord.slash_command(
        name="音樂指令幫助",
        description="顯示音樂機器人的快速上手與控制方式"
    )
    @application_checks.guild_only()
    async def music_help(self, interaction: Interaction):
        await interaction.response.send_message(**component_kwargs(MusicHelpPage.get_components()))


def setup(bot):
    bot.add_cog(Music_help(bot))
