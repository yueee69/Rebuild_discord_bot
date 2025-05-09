from nextcord import Interaction

from models.item_manager import ItemManager

class MainHandler:
    def __init__(self):
        self.item_manager = ItemManager()
        
    async def on_click(self, interaction: Interaction):
        from views import item_crad_check_view
        
        status = interaction.data['custom_id']
        user_item = self.item_manager.get_user(interaction.user.id)
        user_item.protect = eval(status)

        embed, view, ephemeral, content = item_crad_check_view.Create.get_components(interaction)

        await interaction.response.edit_message(
            **({"embed": embed} if embed else {}),
            **({"view": view} if view else {}),
            **({"content": content} if content else {})
        )