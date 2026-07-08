from .base import CoinBase

from managers.user_manager import User, UserManager

class SalmonCoin(CoinBase):
    COIN_TYPE = "鮭魚幣"
    COIN_ID = "salmon_coin"

    def __init__(self, user_id: str | int):
        self.user_id = user_id

    def get_coin_info(self) -> tuple[str, str]:
        user, status = UserManager().get_user(self.user_id)
        if user:
            return (self.COIN_TYPE, user.coin)
        return (self.COIN_TYPE, "無資料")

    def get_button_info(self) -> tuple[str, str, bool]:
        return (self.COIN_TYPE, self.COIN_ID, self.find_user())

    def find_user(self) -> bool:
        user, status = UserManager().get_user(self.user_id)
        return bool(user)
    
    def user_data(self) -> list[User]:
        return list(UserManager().UserDatas.values())
