from abc import ABC, abstractmethod
from enum import Enum

class CheckStatus(Enum):
    OK = 0
    FORTUNE_NOT_ENOUGH = 1
    TIMES_TOO_LOW = 2
    TIMES_TOO_HIGH = 3
    TIMES_IS_VAILD = 4

class LotteryPool(ABC):
    # 這裡搞抽象
    PRICE_PER_LOTTERY = 0
    MIN_LOTTERY = 1
    MAX_LOTTERY = 1

    @abstractmethod
    def check_resource(self, userData: object, times: int):
        pass

    @abstractmethod
    def deduct_fortune(self, userData: object, times: int):
        pass


class NormPool(LotteryPool):
    PRICE_PER_LOTTERY = 1
    MIN_LOTTERY = 1
    MAX_LOTTERY = 25

    def check_resource(self, userData: object, times: int) -> tuple[CheckStatus, str, int]:
        try:
            times = int(times)
        except:
            return(CheckStatus.TIMES_IS_VAILD, f"「** {times} **」不是一個有效數字", 0)
        
        if times < self.MIN_LOTTERY:
            return (CheckStatus.TIMES_TOO_LOW, f"你的抽抽次數不可以低於 **{self.MIN_LOTTERY}**", 0)
        if times > self.MAX_LOTTERY:
            return (CheckStatus.TIMES_TOO_HIGH, f"你的抽抽次數不可以超過 **{self.MAX_LOTTERY}**", 0)
        if userData.fortune < times * self.PRICE_PER_LOTTERY:
            return (CheckStatus.FORTUNE_NOT_ENOUGH, f"你的陽壽不夠，還缺 **{times * self.PRICE_PER_LOTTERY - userData.fortune}** 陽壽", 0)
        return (CheckStatus.OK, "", times)
        

    def deduct_fortune(self, userData: object, times: int):
        userData.fortune -= times * self.PRICE_PER_LOTTERY

class ItemPool(LotteryPool):
    PRICE_PER_LOTTERY = 5

    def check_resource(self, userData: object, times: int) -> tuple[CheckStatus, str]:
        if userData.fortune < times * self.PRICE_PER_LOTTERY:
            return (CheckStatus.FORTUNE_NOT_ENOUGH, f"你的陽壽不夠，還缺 **{times * self.PRICE_PER_LOTTERY - userData.fortune}** 陽壽")
        return (CheckStatus.OK, "")

    def deduct_fortune(self, userData: object, times: int):
        userData.fortune -= self.PRICE_PER_LOTTERY


class XtalPool(LotteryPool):
    PRICE_PER_LOTTERY = 5
    MIN_LOTTERY = 1
    MAX_LOTTERY = 25

    def check_resource(self, userData: object, times: int) -> tuple[CheckStatus, str]:
        if times < self.MIN_LOTTERY:
            return (CheckStatus.TIMES_TOO_LOW, f"你的抽抽次數不可以低於 **{self.MIN_LOTTERY}**")
        if times > self.MAX_LOTTERY:
            return (CheckStatus.TIMES_TOO_HIGH, f"你的抽抽次數不可以超過 **{self.MAX_LOTTERY}**")
        if userData.fortune < times * self.PRICE_PER_LOTTERY:
            return (CheckStatus.FORTUNE_NOT_ENOUGH, f"你的陽壽不夠，還缺 **{times * self.PRICE_PER_LOTTERY - userData.fortune}** 陽壽")
        return (CheckStatus.OK, "")

    def deduct_fortune(self, userData: object, times: int):
        userData.fortune -= times * self.PRICE_PER_LOTTERY
