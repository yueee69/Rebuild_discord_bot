import nextcord

from utils.general import Toolkit
from .BASIC_VIEW import BASIC_VIEW

class Create:
    @staticmethod
    def result(context: object) -> BASIC_VIEW:
        embed = nextcord.Embed(
            title = "成功施加身分組！", 
            description = f"{context.target_user.display_name} 被你施加了 {context.add_role.mention}！", 
            color = Toolkit.randomcolor()
        )
        
        embed.set_thumbnail(url = "https://media.tenor.com/Ym6VeAcZoTcAAAAi/aaaah-cat.gif")
        return BASIC_VIEW.views(embed = embed)