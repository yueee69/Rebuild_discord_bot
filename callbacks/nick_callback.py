from nextcord import Interaction

from profile_management import main_driver
from callbacks.profile_response import send_profile_components

class Main_handler:
    @staticmethod
    async def nick_result(name: str, interaction: Interaction, service: str, user: object):
        comp = await main_driver.Driver().get(
            interaction = interaction,
            service = service,
            target_user = user,
            nick_name = name
            )

        await send_profile_components(interaction, comp)
