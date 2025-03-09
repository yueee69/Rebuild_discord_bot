from models.air_manager import AirManager
from .base import BaseRanking

class Air_rank(BaseRanking):
    def __init__(self, interaction):
        super().__init__(
            interaction = interaction, 
            manager = AirManager(), 
            display_attr = "gain", 
            thumbnail = "https://cdn.discordapp.com/emojis/1341750547283185765.webp", 
            title = "空氣數量"
            )