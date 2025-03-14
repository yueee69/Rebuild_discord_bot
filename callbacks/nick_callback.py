from nextcord import Interaction

from profile_management import main_driver

class Main_handler:
    @staticmethod
    async def nick_result(name: str, interaction: Interaction, service: str, user: object):
        comp = await main_driver.Driver().get(
            interaction = interaction,
            service = service,
            target_user = user,
            nick_name = name
            )

        embed, view, ephemeral, content = comp[0]
        await interaction.followup.send(
                ephemeral=ephemeral,
                **({"embed": embed} if embed else {}),
                **({"view": view} if view else {}),
                **({"content": content} if content else {})
            )


        for embed, view, ephemeral, content in comp[1:]:
            await interaction.followup.send(
                ephemeral=ephemeral,
                **({"embed": embed} if embed else {}),
                **({"view": view} if view else {}),
                **({"content": content} if content else {})
            )
