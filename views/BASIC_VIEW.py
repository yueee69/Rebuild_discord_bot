from nextcord import Embed
from nextcord.ui import View

from utils.general import Toolkit

class BASIC_VIEW:
    @staticmethod
    def views(embed: Embed = None, view: View = None, ephemeral: bool = False, content: str = None) -> tuple[Embed, View, bool ,str]:
        if embed:
            hour, minute, period = Toolkit.get_period_time()
            embed.set_footer(text=f'{period} {hour}:{minute} (GMT+8)') #加上時間戳
        return (embed, view, ephemeral, content)