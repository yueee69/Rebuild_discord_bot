import nextcord
from nextcord.ui import View

from .BASIC_VIEW import BASIC_VIEW

class Error:
    @staticmethod
    def error(
        title = "噢噢...需要的操作暫時無法完成",
        due: str = "Unknown Error :(", 
        thumbnail: str = "",
        color: nextcord.Colour = nextcord.Colour.red(),
        view: View = None
    ) -> BASIC_VIEW:
        
        embed = nextcord.Embed(title = title,description=f"• {due}", color = color)
        embed.set_thumbnail(url = thumbnail)
        return BASIC_VIEW.views(
            embed = embed,
            view = view or View(),
            ephemeral = True,
            with_timestamp = False
            )