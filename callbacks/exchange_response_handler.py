import nextcord
from nextcord import Interaction

from views import exchnge_fortune_views

class ExchangeResponseHandler:
    def __init__(self, check_user_id: int, user_object: object, fortune: int):
        self.check_user_id = int(check_user_id)
        self.user_object = user_object
        self.fortune = fortune

    async def on_check(self, interaction: Interaction):
        custom = interaction.data['custom_id']
        await interaction.message.delete()
        embed, view, ephemeral, content = exchnge_fortune_views.Create.exchange_user_callback(interaction, custom, self.fortune, self.user_object)

        await interaction.response.send_message(
            ephemeral=ephemeral, 
            **({"embed": embed} if embed else {}),
            **({"view": view} if view else {}),
            **({"content": content} if content else {})
        )
    