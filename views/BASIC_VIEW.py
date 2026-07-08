from nextcord import Embed
from nextcord.ui import View

from utils.general import Toolkit

class BASIC_VIEW:
    @staticmethod
    def views(
        embed: Embed = None,
        view: View = None,
        ephemeral: bool = False,
        file: object = None,
        content: str = None,
        clear_view: bool = False,
        with_timestamp: bool = True
    ) -> tuple[Embed, View, bool ,str]:
        if clear_view:
            view = View()

        if embed and with_timestamp:
            hour, minute, period = Toolkit.get_period_time()
            embed.set_footer(text=f'{period} {hour}:{minute}') #加上時間戳

        if file:
            return (embed, view, ephemeral, content, file)
        return (embed, view, ephemeral, content)