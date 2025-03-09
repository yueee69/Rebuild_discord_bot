import nextcord
from nextcord import Interaction

from .BASIC_VIEW import BASIC_VIEW
from .PAGE_EMBED_CREATER import get_paginated_embed 

from utils.general import Toolkit
from models.lottery_manager import LotteryManager

class Create:
    @staticmethod
    def get_components(historyData: object, interaction: Interaction) -> BASIC_VIEW:
        maps = {
            False: Create.No_file,
            True: Create.File_list
        }
        return maps.get(bool(historyData.get_items()))(historyData, interaction)

    @staticmethod
    def No_file(historyData: object, interaction: Interaction) -> BASIC_VIEW:
        embed = nextcord.Embed(
            title = f'以下是 {interaction.user.display_name} 的抽獎歷史紀錄',
            description = '無紀錄', 
            color = Toolkit.randomcolor()
            )
        return BASIC_VIEW.views(embed = embed)

    @staticmethod
    def File_list(historyData: object, interaction: Interaction) -> BASIC_VIEW:
        LotteryInfo = LotteryManager().get_user(interaction.user.id)
        title = f'以下是 {interaction.user.display_name} 的抽獎歷史紀錄'
        description = f'墊抽數 : **__{LotteryInfo.lottery_accumulation}__** \n總抽數 : **__{LotteryInfo.lottery_total}__**'
        img = "https://cdn.discordapp.com/emojis/1053886138990997664.webp"

        return get_paginated_embed(historyData.get_items(), title, description, img)