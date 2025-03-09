from nextcord import Interaction

from .coin import Coin_rank
from .air import Air_rank

class Driver:
    maps = {
            "coin": Coin_rank,
            "air": Air_rank
        }
    @staticmethod
    def get(selectValue: str, interaction: Interaction):       
        return Driver.maps.get(selectValue)(interaction).get_components()