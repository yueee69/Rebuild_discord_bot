from nextcord import Interaction

from Lottery.main_driver import Driver

class Main_handler:
    @staticmethod
    async def result(interaction: Interaction, pool: str, user: object, times: int):
        embed, view, ephemeral, content = Driver().get(pool, user, times)

        await interaction.response.send_message(
            ephemeral=ephemeral, 
            **({"embed": embed} if embed else {}),
            **({"view": view} if view else {}),
            **({"content": content} if content else {})
        )
        return
    