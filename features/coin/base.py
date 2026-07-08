from abc import ABC, abstractmethod

class CoinBase(ABC):
    COIN_TYPE = ""

    @abstractmethod
    def get_coin_info(self) -> tuple[str, str]:
        pass

    @abstractmethod
    def get_button_info(self) -> tuple[str, str, bool]:
        pass

    @abstractmethod
    def find_user(self) -> bool:
        """
        返回用戶是否在對應存檔中
        """
        pass

    @abstractmethod
    def user_data(self) -> list[object]:
        """
        返回對應的用戶data
        """
        pass