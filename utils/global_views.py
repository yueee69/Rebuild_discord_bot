import nextcord

from nextcord import Embed
from nextcord.ui import View

class UserCallback:
    @staticmethod
    def get_Components(status: bool, components: Embed):
        """
        Params:
            status: 從UserManager打開返回的狀態值
            components: 如果在這裡沒有找到函式，就返回原本該回應的view組件
        """
        comps = {
            "NotFoundAndNeedToRegister": UserCallback.user_not_found_embed()
        }
        return comps.get(status, components)
    
    @staticmethod
    def user_not_found_embed() -> tuple[Embed, View, bool]:
        """
        Returns:
            tuple[Embed, View, bool]: 
                - Embed: 錯誤訊息的 Embed 物件
                - View: 按鈕或互動視圖（目前為 None，但可以擴充）
                - bool: 訊息別人是否可見
        """
        embed = Embed(title="捕捉到了一個小錯誤~", colour=nextcord.Colour.red())
        embed.add_field(name="• 您尚未登記", value="請使用 /用戶資訊 註冊資料！", inline=False)
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/695989213799252018.webp")

        return embed, None, True
    
class RpgCallback:
    pass