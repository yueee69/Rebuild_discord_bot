"這個模塊用來返回顯示大量資料 將大量資料塞進embed並做成可翻頁式 請使用get_paginated_embed取得view組件"

import nextcord
from nextcord import Interaction
from nextcord.ui import View, Button, button

from .BASIC_VIEW import BASIC_VIEW
from utils.general import Toolkit

class EmbedPaginator(View):
    def __init__(self, data_list: list[dict], title: str, description: str, img: str , max_items: int, per_page: int = 5):
        super().__init__(timeout = None)
        self.title = title
        self.per_page = per_page
        self.description = description
        self.color = Toolkit.randomcolor()
        self.img = img
        self.max_items = max_items if max_items is not None else len(data_list)
        self.data_list = data_list[:self.max_items]
        self.page = 0
        self.max_page = (len(self.data_list) - 1) // per_page

        self.update_button_states()

    def get_page_content(self):
        """取得當前頁面的內容"""
        start = self.page * self.per_page
        end = min(start + self.per_page, self.max_items)

        page_data = self.data_list[start:end]

        embed = nextcord.Embed(title=self.title, description = self.description, color = self.color)
        embed.set_thumbnail(url = self.img)
        embed.set_footer(text=f"頁數: {self.page + 1} / {self.max_page + 1}")

        if not page_data:
            embed.description = "無內容"
        else:
            for entry in page_data:
                item = entry.get("item", "未知獎品")
                time = entry.get("time", "未知時間")
                embed.add_field(name = f'{item}\n{time}', value = '────────────────────', inline = False)

        return embed

    def update_button_states(self):
        """根據當前頁數更新按鈕狀態"""
        self.previous_page.disabled = self.page == 0
        self.next_page.disabled = self.page == self.max_page

    async def update_message(self, interaction: Interaction):
        """更新 Embed 內容與按鈕狀態"""
        self.update_button_states()
        await interaction.response.edit_message(embed=self.get_page_content(), view=self)

    @button(label="◀", style=nextcord.ButtonStyle.primary)
    async def previous_page(self, button: Button, interaction: Interaction):
        """上一頁"""
        if self.page > 0:
            self.page -= 1
            await self.update_message(interaction)

    @button(label="▶", style=nextcord.ButtonStyle.primary)
    async def next_page(self, button: Button, interaction: Interaction):
        """下一頁"""
        if self.page < self.max_page:
            self.page += 1
            await self.update_message(interaction)

    @button(label="關閉", style=nextcord.ButtonStyle.danger)
    async def close_embed(self, button: Button, interaction: Interaction):
        """關閉 Embed"""
        await interaction.response.defer()
        await interaction.message.delete()

def get_paginated_embed(data_list: list[dict], title="📜 資訊列表", description: str = '', img: str = None,max_items: int = None):
    """建立 EmbedPaginator，並透過 BASIC_VIEW 統一處理 Embed"""
    paginator = EmbedPaginator(data_list, title, description, img, max_items)

    embed = paginator.get_page_content()
    
    components = BASIC_VIEW.views(embed=embed, view=paginator)

    return components