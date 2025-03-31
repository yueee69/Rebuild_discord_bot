import webcolors
from Ai import chatgpt

from views.role_display_view import Create

from nextcord import Interaction

from core import constants

class Main_hindler:
    @staticmethod
    def main(interaction: Interaction):
        roles = Role_tool.get_role_info(interaction.guild)
        return Create.get_components(roles, interaction)
    
class Role_tool:

    SYSTEM = """
    以下是我給你的一組列表 你必須對應列表回復對應的顏色，可以加一些你的創意並且不要太死板，*同樣的顏色必須名字保持一致！*
    注意！ ****回傳格式只能是中文化的列表****(順序、數量都必須保持原樣) 並且不要加其他的訊息 否則我會eval失敗！
    "⚠️ 注意：如果你的回應違反格式，我的程式將視為「錯誤回應」，並丟棄你的回答！"
    """
    DO_NOT_ROLE = constants.DO_NOT_ROLE 

    @staticmethod
    def get_role_info(guild: object) -> list[dict]:
        """
        把role轉換成符合PAGE_EMBED_CREATER的設計
        """
        role_data = []
        eng_names = []
        roles = Role_tool._filter_vaild_roles(guild.roles)
        for role in roles:
            hex_color = Role_tool._get_role_hex_color(role)
            eng_name = Role_tool._get_eng_name(hex_color)

            role_data.append((role, hex_color, eng_name))
            eng_names.append(eng_name)

        chinese_names = Role_tool._get_chinese_name(eng_names)

        result = []
        for i, (role, hex_color, eng_name) in enumerate(role_data):
            chinese_name = chinese_names[i]  # 對應的中文顏色

            result.append({
                "item": role.name,
                "time": f"顏色名稱: {chinese_name} ({eng_name})\nHEX: {hex_color}"
            })
        return result
        
    @staticmethod
    def _filter_vaild_roles(roles: list) -> list:
        result = []
        for role in roles:
            if role.name not in Role_tool.DO_NOT_ROLE and role.name != "@everyone" and not role.is_bot_managed():
                result.append(role)
        return result

    @staticmethod
    def _get_role_hex_color(role: object) -> str:
        """
        返回身分組的 Hex 顏色
        """
        rgb = role.color.to_rgb()
        return '#{:02x}{:02x}{:02x}'.format(*rgb)
    
    @staticmethod
    def _get_eng_name(hex_color: str) -> str:
        try:
            return webcolors.hex_to_name(hex_color)
        except ValueError:
            rgb_color = webcolors.hex_to_rgb(hex_color)
            return min(
                webcolors.CSS3_HEX_TO_NAMES.items(),
                key=lambda color: sum((rgb_color[i] - webcolors.hex_to_rgb(color[0])[i]) ** 2 for i in range(3))
            )[1]
 
    @staticmethod
    def _get_chinese_name(hex_eng_name: list) -> str:
        response = chatgpt.Tool().ask(
            system_info = Role_tool.SYSTEM,
            question = str(hex_eng_name),
            temp = 0.0
        )
        return eval(response)