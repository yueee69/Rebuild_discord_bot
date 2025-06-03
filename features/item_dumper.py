"""
這裡用於將道具分配到用戶的資料 例如: 抽獎獎品、購買道具等 不適用rpg
"""
import nextcord
from nextcord import Interaction
from models.user_manager import User, UserManager

class ItemRewardAllocator:
    """
    自動分配道具，只需要傳入初始化資料即可
    例如:

    params:
        items: list[str] 傳入字串組成的獎品
        user_id: 用戶discord_id
        method: 需要印在log_embed上的字 例如: "XXX買了" "XXX抽到了"
        interaction: discord interaction
    """
    LOG_CHANNEL_ID = 1183431186161340466
    ACTIONS = {
            "陽壽": "fortune",
            "鮭魚幣": "coin"
        }

    def __init__(
        self,
        *,
        items: list[str],
        user_id: int | str,
        interaction: Interaction,
        method: str = "得到了",
        send_log: bool = True
    ):
        self.items = items
        self.user_id = user_id
        self.method = method
        self.interaction = interaction
        self.send_log = send_log

        self.user, _ = UserManager().get_user(self.user_id)
        self.bot = self.interaction.client

    async def apply(self) -> None:
        """
        這裡分為三種道具:
        1. 陽壽
        2. 鮭魚幣
        3. 其餘道具
        其中1和2會直接apply，但3會傳訊息到log頻道中
        """
        unknown_items = []

        for item in self.items:
            matched = False
            for key, attr in self.ACTIONS.items():
                if key in item:
                    num = self._extract_number(item)
                    self._allocate(num, attr)
                    self._log(item)
                    matched = True
                    break

            if not matched:
                unknown_items.append(item)

        if unknown_items and self.send_log:
            await self.send_log_message(unknown_items)

    def _extract_number(self, item: str) -> int:
        """
        將數目從字串中提取出來
        """
        digits = ''.join(text for text in item if text.isdigit())
        return int(digits) if digits else 0
    
    def _allocate(self, num: int, attr: str) -> None:
        setattr(self.user, attr, getattr(self.user, attr) + num)

    def _log(self, name: str) -> None:
        user_name = self.interaction.user.display_name
        print(f"(ItemRewardAllocator) {user_name} {self.method} {name}")

    async def send_log_message(self, items: list[str]) -> None:
        name = self.interaction.user.display_name

        embed = nextcord.Embed(
            title = f"{name} {self.method}：",
            description = "\n".join(item for item in items)
        )
        await self.bot.get_channel(self.LOG_CHANNEL_ID).send(embed = embed)