import nextcord
from nextcord import Interaction, Embed
from nextcord.ui import Modal, TextInput, Button, View

from new_bot.callbacks import lottery_handler
from new_bot.utils.general import Toolkit
from .BASIC_VIEW import BASIC_VIEW

import asyncio
from typing import Union

class get_components:
    @staticmethod
    async def lottery_views(choices: str, interaction: Interaction, user: object) -> Union[Modal, tuple[Embed, View, bool], BASIC_VIEW]:
        if choices == 'item_pool':
            await Item_pool_components().make_view(interaction, user)
            
        views = {
            "norm_pool": Norm_pool_components(user),
            "xtal_pool": Xtal_pool_components().make_view(interaction, user),
        }

        view_creator = views.get(choices, lambda: BASIC_VIEW.views())
      
        return view_creator

class Norm_pool_components(Modal):
    def __init__(self, user):
        super().__init__(title="陽壽人陽壽魂(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧")
        self.NORM_POOL_PRICE = 1
        self.MIN_LOTTERY_TIMES = 1
        self.MAX_LOTTERY_TIMES = 25
        self.user = user

        self.input_field = TextInput(
            label="陽壽",
            placeholder=f"輸入要投入的陽壽！({self.MIN_LOTTERY_TIMES} ~ {self.MAX_LOTTERY_TIMES})",
            required=True,
            style=nextcord.TextInputStyle.short
        )

        self.callback = self.on_submit

        self.add_item(self.input_field)
        
    async def on_submit(self, interaction: Interaction):
        times = interaction.data['components'][0]['components'][0]['value']
        await lottery_handler.Main_handler().result(interaction, "norm_pool",self.user, times)

class Xtal_pool_components:
    def __init__(self):
        self.XTAL_LOTTERY_PRICE = 5
    
    def make_view(self, interaction: Interaction, user: object) -> tuple[Embed, View]:
        userXtalData, xtalData = Toolkit.open_jsons("user_xtaldata.json", "xtal_lottery.json")
        emoji = interaction.client.get_emoji

        one_button = Button(label='1抽', custom_id='1', style=nextcord.ButtonStyle.success, emoji=emoji(1272223956228767854))
        five_button = Button(label='5抽', custom_id='5', style=nextcord.ButtonStyle.success, emoji=emoji(1272223954261512314))
        ten_button = Button(label='10抽', custom_id='10', style=nextcord.ButtonStyle.success, emoji=emoji(1272223938772074517))
        lottery_button_1 = Button(label='兌換王石', custom_id='exchange_xtal', style=nextcord.ButtonStyle.blurple, emoji=emoji(1272545890967617658), row=1)
        lottery_button_2 = Button(label='兌換免費抽取', custom_id='exchange_free_lottery', style=nextcord.ButtonStyle.blurple, emoji=emoji(1272545900681498705), row=1)
        lottery_button_3 = Button(label='查看臨時背包', custom_id='check_xtal_bag', style=nextcord.ButtonStyle.blurple, emoji=emoji(1206825617912504380), row=2)

        view = View()
        view.add_item(one_button)
        view.add_item(five_button)
        view.add_item(ten_button)
        view.add_item(lottery_button_1)
        view.add_item(lottery_button_2)
        view.add_item(lottery_button_3)

        async def lottery_callback(interaction: Interaction, times: int):
            await lottery_handler.Driver.Xtal_pool_driver(interaction, times)

        async def exchange_xtal_callback(interaction: Interaction):
            await lottery_handler.Driver.exchange_xtal(interaction)

        async def exchange_free_lottery_callback(interaction: Interaction):
            await lottery_handler.Driver.exchange_free_lottery(interaction)

        async def check_xtal_bag_callback(interaction: Interaction):
            await lottery_handler.Driver.check_xtal_bag(interaction)

        one_button.callback = lambda i: lottery_callback(i, 1)
        five_button.callback = lambda i: lottery_callback(i, 5)
        ten_button.callback = lambda i: lottery_callback(i, 10)
        lottery_button_1.callback = exchange_xtal_callback
        lottery_button_2.callback = exchange_free_lottery_callback
        lottery_button_3.callback = check_xtal_bag_callback

        # 建立 Embed
        embed = nextcord.Embed(
            title='王石抽獎',
            description=f'{interaction.user.mention} 你目前有 {userXtalData[str(interaction.user.id)]["free"]} 次免費抽取的機會',
            color=Toolkit.randomcolor()
        )
        embed.set_thumbnail(url='https://cdn.discordapp.com/emojis/1206653152795959388.webp')
        embed.add_field(name='抽獎價格：', value='**--------------------**', inline=False)
        embed.add_field(name=f'{emoji(1272223956228767854)} 1抽', value='5陽壽', inline=False)
        embed.add_field(name=f'{emoji(1272223954261512314)} 5抽', value='25陽壽', inline=False)
        embed.add_field(name=f'{emoji(1272223938772074517)} 10抽', value='50陽壽', inline=False)
        embed.add_field(name='--------------------', value='**__限時加倍__**：', inline=False)
        embed.add_field(name=f'{xtalData[1]["item"]} 機率限時提升！', value=f'(剩餘{7-xtalData[1]["date"]}天)', inline=False)
        embed.add_field(name='抽獎規則：', value=f"{self.XTAL_LOTTERY_PRICE}陽壽一抽，價格不定時改變\n(優先使用免費抽取次數)\n抽獎後，王石會進入**__臨時背包__**\n需要用戶點選按鈕自行領出\n或是使用五個獎品**__兌換一次免費抽獎__**", inline=False)

        return BASIC_VIEW.views(embed=embed, view=view)

class Item_pool_components:
    def __init__(self):
        pass

    async def make_view(self, interaction: Interaction, user: object) -> BASIC_VIEW:
        await lottery_handler.Main_handler().result(interaction, "item_pool", user, 1)

    @staticmethod
    def result(prizes: list) -> BASIC_VIEW:
        embed = nextcord.Embed(title="✨ 這波純賺不虧 ✨", color=Toolkit.randomcolor())
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/747551295489179778.gif")
        for item in prizes:
            embed.add_field(name=f"🎁 {item}", value="", inline=False)
        return BASIC_VIEW.views(embed=embed)
    
class Result:
    @staticmethod
    def result(prizes: list) -> BASIC_VIEW:
        embed = nextcord.Embed(title = "🔥你的手氣逆天了！", description = "以下是你抽取的獎品", color = Toolkit.randomcolor())
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/747551295489179778.gif")
        for item in prizes:
            embed.add_field(name = item, value = '', inline = False)
        return BASIC_VIEW.views(embed = embed)
