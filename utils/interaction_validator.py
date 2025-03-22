import nextcord
from nextcord import Interaction

from views.ERROR import Error

class InteractionValidator:

    ADMIN_ID = {579618807237312512}

    """驗證與交互相關的權限"""
    @staticmethod
    async def check_authorization(old_interaction: Interaction, new_interaction: Interaction) -> bool:
        """
        檢查別人有沒有偷點用戶的view

        Params:
            old_interaction: 用戶最先打開的interaction
            new_interaction: 用戶後續和view交互的interaction
        """

        if new_interaction.user.id == old_interaction.user.id or new_interaction in InteractionValidator.ADMIN_ID:
            return True  # 使用者是發起人，或是管理員，可以通過驗證

        await InteractionValidator.send_error_response(new_interaction)            
        return False
    
    @staticmethod
    async def send_error_response(interaction: Interaction):
        embed, view, ephemeral, content = Error.error(
            title="你偷壞壞",
            due="沒事點別人的指令幹嘛！？"
        )

        await interaction.response.send_message(
            ephemeral = ephemeral,
                embed = embed
        )