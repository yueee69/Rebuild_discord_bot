import nextcord
from nextcord import Interaction
from nextcord.ext import application_checks

from commands.base_command import Cog_Extension
from core import constants
from views.character_exp_calculator_view import CharacterExpCalculatorModal


class CharacterExpCalculator(Cog_Extension):
    def __init__(self, bot):
        super().__init__(bot)

    @nextcord.slash_command(
        name="角色經驗計算機",
        description="計算主線經驗可推進的角色等級",
        guild_ids=constants.ENABLE_COMMAND_USE_GUILDS,
    )
    @application_checks.guild_only()
    async def character_exp_calculator(self, interaction: Interaction):
        await interaction.response.send_modal(CharacterExpCalculatorModal())


def setup(bot):
    bot.add_cog(CharacterExpCalculator(bot))
