import nextcord
import nextcord
from nextcord import Interaction

from views import exchnge_fortune_views

class ExchangeResponseHandler:
    def __init__(self, check_user_id: int, user_object: object, fortune: int):
        self.check_user_id = int(check_user_id)
        self.user_object = user_object
        self.fortune = fortune

    async def on_check(self, interaction: Interaction):
        if interaction.user.id != self.check_user_id:
            await interaction.response.send_message("這不是你的兌換確認按鈕。", ephemeral=True)
            return

        custom = interaction.data['custom_id']
        embed, view, ephemeral, content = exchnge_fortune_views.Create.exchange_user_callback(interaction, custom, self.fortune, self.user_object)

        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=ephemeral)

        if interaction.message:
            try:
                await interaction.message.delete()
            except (nextcord.NotFound, nextcord.Forbidden, nextcord.HTTPException):
                pass

        await interaction.followup.send(
            **({"embed": embed} if embed else {}),
            **({"view": view} if view else {}),
            **({"content": content} if content else {}),
            ephemeral=ephemeral,
        )
