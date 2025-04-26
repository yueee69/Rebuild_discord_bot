import nextcord
from nextcord import Interaction

from utils.general import Toolkit
from utils.discord_model import GenericModal
from .BASIC_VIEW import BASIC_VIEW
from callbacks import nick_callback

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
        await nick_callback.Main_handler.nick_result(name, interaction, self.service, self.user)
        
    @staticmethod
    def result(context: object) -> list[BASIC_VIEW]:
        embed = nextcord.Embed(title = "成功修改暱稱！", description = f"成功把 {context.target_user.name} 改名成 {context.nick_name}", color = Toolkit.randomcolor())
        embed.set_thumbnail(url = "https://media.tenor.com/Ym6VeAcZoTcAAAAi/aaaah-cat.gif")
        return BASIC_VIEW.views(embed = embed)