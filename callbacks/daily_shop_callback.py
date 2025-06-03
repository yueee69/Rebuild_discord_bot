from nextcord import Interaction

from views import BASIC_VIEW

class Message:
    @staticmethod
    async def send(interaction: Interaction, comp: BASIC_VIEW):
        embed, view, ephemeral, content = comp
        await interaction.response.send_message(
                ephemeral = ephemeral,
                **({"embed": embed} if embed else {}),
                **({"view": view} if view else {}),
                **({"content": content} if content else {})
            )

    @staticmethod
    async def edit(interaction: Interaction, comp: BASIC_VIEW):
        embed, view, ephemeral, content = comp
        await interaction.response.edit_message(
                **({"embed": embed} if embed else {}),
                **({"view": view} if view else {}),
                **({"content": content} if content else {})
            )