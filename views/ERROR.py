import nextcord

from .BASIC_VIEW import BASIC_VIEW

class Error:
    @staticmethod
    def error(title = "噢噢...發生了一點小問題~",due: str = "Unknown Error :(", thumbnail: str = "https://cdn.discordapp.com/emojis/695989213799252018.webp") -> BASIC_VIEW:
        embed = nextcord.Embed(title = title,description=f"• {due}", color=nextcord.Colour.red())
        embed.set_thumbnail(url = thumbnail)
        return BASIC_VIEW.views(embed = embed, ephemeral = True)