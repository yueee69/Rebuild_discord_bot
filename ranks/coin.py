from models.user_manager import UserManager
from .base import BaseRanking

class Coin_rank(BaseRanking):
    def __init__(self, interaction):
        super().__init__(
            interaction = interaction, 
            manager = UserManager(), 
            display_attr = "gain", 
            thumbnail = "https://cdn.discordapp.com/emojis/1168906560626495488.webp", 
            title = "已獲取鮭魚幣"
            )
