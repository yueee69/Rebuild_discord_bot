from profile_management.main_driver import Driver
from views import assign_role_view

from utils.interaction_validator import InteractionValidator

from nextcord import Interaction

from dataclasses import dataclass
import random

@dataclass
class State_manager:
    interaction: object = None
    target: object = None
    role: object = None
    service: str = ""
    display_color: bool = False


class Main_handler:
    @staticmethod
    async def main(data: State_manager):
        comp = await Driver().get(
            interaction = data.interaction,
            service = data.service,
            target_user = data.target,
            add_role = data.role,
            display_color = data.display_color
        )

        embed, view, ephemeral, content = comp[0]
        await data.interaction.message.delete()
        await data.interaction.response.send_message(
                ephemeral = ephemeral,
                **({"embed": embed} if embed else {}),
                **({"view": view} if view else {}),
                **({"content": content} if content else {})
            )

        if len(comp) > 0:
            for embed, view, ephemeral, content in comp[1:]:
                await data.interaction.followup.send(
                    ephemeral = ephemeral,
                    **({"embed": embed} if embed else {}),
                    **({"view": view} if view else {}),
                    **({"content": content} if content else {})
                )
    
    
class SelectHandler:
    async def get_components(self, data: State_manager):
        return assign_role_view.Select_view(SelectHandler.__random_display_color()).get_components(data)

    @staticmethod
    async def select_color(interaction: Interaction, data: State_manager):
        """用戶選擇完是否顯示顏色 然後交給main處理"""
        if not await InteractionValidator.check_authorization(data.interaction, interaction):
            return

        data.display_color = bool(eval(interaction.data["values"][0])) #將str轉成bool
        data.interaction = interaction

        await Main_handler.main(data)

    @staticmethod
    def __random_display_color() -> str:
        """隨機產生是否顯示顏色"""
        return random.choice(["2", "-1"])
    