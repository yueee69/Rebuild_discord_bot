from .salmon_coin import SalmonCoin

class CoinManager:
    COINS = {
        "salmon_coin": SalmonCoin
    }
    DISABLED_COIN_IDS = {"rpg_coin"}
    DISABLED_COIN_NAMES = {"RPG金幣", "RPG 金幣"}

    def __init__(self, coin: str, user_id: str | int):
        self.coin = coin
        self.user_id = user_id

    def find_user_in_data(self) -> bool:
        coin = self.COINS.get(self.coin)
        if coin and self._is_enabled(coin):
            return coin(self.user_id).find_user()
        return False

    def get_user_data(self) -> list[object]:
        """
        返回一個幣種相關的manager data
        """
        data = self.COINS.get(self.coin)
        if data and self._is_enabled(data):
            return data(self.user_id).user_data()
        return []

    def get_coin_name(self) -> str:
        coin = self.COINS.get(self.coin)
        if coin and self._is_enabled(coin):
            return coin.COIN_TYPE
        return ""
    
    def get_all_coin_data(self) -> list[tuple[str, str]]:
        result = []
        coins = self._enabled_coins()
        for coin in coins:
            result.append(
                coin(self.user_id).get_coin_info()
            )
        
        return result
    
    def get_all_coin_button_info(self) -> list[tuple[str, str, bool]]:
        result = []
        coins = self._enabled_coins()
        for coin in coins:
            result.append(
                coin(self.user_id).get_button_info()
            )
        
        return result

    @classmethod
    def _enabled_coins(cls):
        return [
            coin
            for coin_id, coin in cls.COINS.items()
            if coin_id not in cls.DISABLED_COIN_IDS and cls._is_enabled(coin)
        ]

    @classmethod
    def _is_enabled(cls, coin) -> bool:
        return coin.COIN_TYPE not in cls.DISABLED_COIN_NAMES
