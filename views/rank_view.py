import nextcord
from nextcord import Interaction
from .BASIC_VIEW import BASIC_VIEW

from callbacks.rank_callback import RankSelectHandler

class RankSelect(nextcord.ui.Select):
    def __init__(self):
        options = [
            nextcord.SelectOption(label="金幣排行榜", value="coin"),
            nextcord.SelectOption(label="空氣排行榜", value="air"),
        ]
        super().__init__(placeholder="點我選擇排行種類！", options=options)

    async def callback(self, interaction: Interaction):
        await RankSelectHandler.get_components(interaction, self.values[0])

class RankSelectView(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(RankSelect())

class Create:
    @staticmethod
    def get_components(guild_id: int):
        return BASIC_VIEW.views(view = RankSelectView())