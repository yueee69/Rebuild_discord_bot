import nextcord
from nextcord import Interaction
from nextcord.ui import View, Select

from utils.general import Toolkit
from .BASIC_VIEW import BASIC_VIEW

from new_bot.callbacks import assign_role_callback

class Select_view:
    def __init__(self, random_choice: str) -> BASIC_VIEW:
        self.random_choice = random_choice

    def get_components(self, data: object) -> BASIC_VIEW:
        """返回要不要顯示顏色的選項"""
        return BASIC_VIEW.views(view = ColorSelectView(self.random_choice, data))


class ColorSelectView(View):
    def __init__(self, random_choice: str, data: object):
        super().__init__()
        self.add_item(ColorSelect(random_choice, data))


class ColorSelect(Select):
    def __init__(self, random_choice: str, data: object):
        self.data = data
        self.DISPLAY_COLOR = [
        nextcord.SelectOption(label = "好啊好啊", value = "1", description = "被你指定的用戶會顯示顏色"),
        nextcord.SelectOption(label = "不要", value = "0", description = "啊就不要"),
        nextcord.SelectOption(label = "隨便", value = random_choice, description = "隨便。")
    ]
        super().__init__(placeholder = "你要不要顯示顏色？", options = self.DISPLAY_COLOR)
        
    async def callback(self, interaction: Interaction):
        await assign_role_callback.SelectHandler.select_color(interaction, self.data)

class Create:
    @staticmethod
    def result(context: object) -> BASIC_VIEW:
        embed = nextcord.Embed(
            title = "成功施加身分組！", 
            description = context.description, 
            color = Toolkit.randomcolor()
        )
        
        embed.set_thumbnail(url = "https://media.tenor.com/Ym6VeAcZoTcAAAAi/aaaah-cat.gif")
        return BASIC_VIEW.views(embed = embed)
    
