import nextcord
from nextcord import Interaction

from utils.discord_model import GenericModal
from .BASIC_VIEW import BASIC_VIEW
from callbacks.nick_callback import Main_handler

class Create:
    def __init__(self, user, service: str):
        self.user = user
        self.service = service

    def get_components(self) -> BASIC_VIEW:
        return GenericModal(
            title = '輸入要修改的名稱 (:3[__]4',
            input_fields = [
                {
                    "name": "name",
                    "label": "暱稱",
                    "placeholder": "填寫要修改的名稱",
                    "required": True,
                    "style": nextcord.TextInputStyle.short
                }
            ],
            custom_callback = self.on_submit
        )
    async def on_submit(self, interaction: Interaction, response: dict):
        name = response["name"]
        await Main_handler.nick_result(name, interaction, self.service, self.user)
        
    @staticmethod
    def result(context: object) -> BASIC_VIEW:
        embed = nextcord.Embed(title = "成功")
        return BASIC_VIEW.views(embed = embed)