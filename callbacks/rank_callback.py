import nextcord
from nextcord import Interaction

from ranks.main_driver import Driver

class RankSelectHandler:
    @staticmethod
    async def get_components(interaction: Interaction, selectValue: str):
        embed, view, ephemeral, content = Driver.get(selectValue, interaction)

        await interaction.response.edit_message(
            **({"embed": embed} if embed else {}),
            **({"view": view} if view else {}),
            **({"content": content} if content else {})
        )