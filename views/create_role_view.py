import nextcord
from nextcord import Interaction
from nextcord.ui import View, Select

from utils.general import Toolkit

from utils.discord_model import GenericModal
from callbacks import create_role_callback

from .BASIC_VIEW import BASIC_VIEW

class Select_view:
    def __init__(self, service: str, color: str) -> BASIC_VIEW:
        self.service = service
        self.color = color

    def get_components(self) -> BASIC_VIEW:
        """返回選擇顏色的 UI View"""
        return BASIC_VIEW.views(view = ColorSelectView(self.service, self.color))


class ColorSelectView(View):
    def __init__(self, service: str, color: str):
        super().__init__()
        self.add_item(ColorSelect(service, color))


class ColorSelect(Select):
    def __init__(self, service: str, color: str):
        self.service = service
        self.color = color
        self.COLOR_OPTIONS = [
        nextcord.SelectOption(label="🎲 交由命運決定！", value = self.color, description="系統隨機分配一個顏色"),
        nextcord.SelectOption(label="🎨 自訂顏色", value="custom", description="輸入 Hex 色碼自訂一個顏色"),
        nextcord.SelectOption(label="🔴 紅色", value="#FF0000"),
        nextcord.SelectOption(label="🔵 藍色", value="#0000FF"),
        nextcord.SelectOption(label="🟢 綠色", value="#00FF00"),
        nextcord.SelectOption(label="🟣 紫色", value="#800080"),
        nextcord.SelectOption(label="🟡 黃色", value="#FFFF00"),
        nextcord.SelectOption(label="⚪ 白色", value="#FFFFFF"),
        nextcord.SelectOption(label="⚫ 黑色", value="#000000"),
        nextcord.SelectOption(label="🟠 橘色", value="#FFA500"),
        nextcord.SelectOption(label="💗 粉色", value="#FFC0CB"),
        nextcord.SelectOption(label="🌊 湖藍色", value="#1E90FF"),
        nextcord.SelectOption(label="🌿 青綠色", value="#008080"),
        nextcord.SelectOption(label="🌅 金色", value="#FFD700"),
        nextcord.SelectOption(label="🌑 暗灰色", value="#2F4F4F"),
        nextcord.SelectOption(label="🩶 銀灰色", value="#C0C0C0"),
        nextcord.SelectOption(label="💩 大便色", value="#6F4E37", description="最天然的顏色(?)"),
        nextcord.SelectOption(label="👾 外星人紫", value="#7D00F0"),
        nextcord.SelectOption(label="🍆 茄子紫", value="#311B92"),
        nextcord.SelectOption(label="🍣 鮭魚粉", value="#FF8C69"),
        nextcord.SelectOption(label="🟤 土壤棕", value="#8B4513"),
        nextcord.SelectOption(label="☄️ 隕石灰", value="#4B4B4B"),
        nextcord.SelectOption(label="🛑 禁止紅", value="#D50000"),
        nextcord.SelectOption(label="🤢 嘔吐綠", value="#A4D55E"),
        nextcord.SelectOption(label="🍵 抹茶綠", value="#A3C585"),
    ]
        super().__init__(placeholder = "點我選擇一個顏色！", options = self.COLOR_OPTIONS, custom_id = service)
        
    async def callback(self, interaction: Interaction):
        await create_role_callback.SelectHandler.select_color(interaction)


class RoleCreateModal(GenericModal):
    def __init__(self, select: str, service: str, is_custom: bool):
        input_fields = get_create_model_files(select, is_custom)
        super().__init__(title="填寫身分組資訊 (´ー`)", input_fields = input_fields, custom_callback = RoleCreateModal.callback, custom_id = f"{service}/{select}")

    @staticmethod
    async def callback(interaction: Interaction, response: dict):
        await create_role_callback.Main_handler.create_role_result(interaction, response)

def get_create_model_files(select: str, is_custom: bool) -> list:
    input_files = [
        {
            "name": "name",
            "label": "身分組名稱",
            "placeholder": "創建的名稱",
            "required": True,
            "style": nextcord.TextInputStyle.short,
        }
    ]
    if is_custom:
        input_files.append(
            {
                "name": "color",
                "label": "使用 Hex 色碼，填寫身分組的顏色！",
                "placeholder": "#1A2B3C",
                "required": True,
                "style": nextcord.TextInputStyle.short,
            }
        )

    return input_files

    
class Create:
    @staticmethod
    def result(context: object) -> BASIC_VIEW:
        embed = nextcord.Embed(title = "成功創建身分組！", description = f"你已經創建 {context.created_role.mention} ！", color = Toolkit.randomcolor())
        embed.set_thumbnail(url = "https://media.tenor.com/Ym6VeAcZoTcAAAAi/aaaah-cat.gif")
        return BASIC_VIEW.views(embed = embed)