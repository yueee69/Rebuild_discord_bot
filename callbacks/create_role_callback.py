from nextcord import Interaction
import random

from utils.general import Toolkit

from views import create_role_view
from profile_management import main_driver

class SelectHandler:
    def __init__(self, service: str):
        self.service = service

    async def get_components(self):
        return create_role_view.Select_view(self.service, SelectHandler.__random_hex_color()).get_components()

    @staticmethod
    async def select_color(interaction: Interaction):
        """處理使用者選擇顏色後的邏輯，返回一個modal"""
        selected_color = interaction.data["values"][0]
        service = interaction.data["custom_id"]
        is_custom = Toolkit.is_custom_color(selected_color)

        modal = create_role_view.RoleCreateModal(selected_color, service, is_custom)
        await interaction.response.send_modal(modal)

    @staticmethod
    def __random_hex_color() -> str:
        """隨機產生 HEX 色碼"""
        return f"#{''.join(random.choices('0123456789ABCDEF', k = 6))}"
    

class Main_handler:
    async def create_role_result(interaction: Interaction, response: dict):
        await interaction.message.delete()

        color = response.get("color", None)
        if not color:
            color = interaction.data["custom_id"].split("/")[1]

        comp = await main_driver.Driver().get(
            interaction = interaction,
            service = interaction.data["custom_id"].split("/")[0],
            create_role_name = response["name"],
            create_role_color = color
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
