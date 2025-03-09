from nextcord import Interaction

from profile_management.main_driver import Driver

class Main_handler:
    @staticmethod
    async def nick_result(name: str, interaction: Interaction, service: str, user: object):
        embed, view, ephemeral, content = await Driver().get(
                                            interaction = interaction,
                                            service = service,
                                            target_user = user,
                                            nick_name = name
                                            )

        await interaction.response.send_message(
            ephemeral=ephemeral, 
            **({"embed": embed} if embed else {}),
            **({"view": view} if view else {}),
            **({"content": content} if content else {})
        )
    