import Lottery.lottery_driver

from views.BASIC_VIEW import BASIC_VIEW

class Driver:
    def __init__(self):
        self.BASIC_PATH = Lottery.lottery_driver.Driver
        self.drivers = {
            "norm_pool": self.BASIC_PATH.norm_pool,
            "item_pool": self.BASIC_PATH.item_pool,
            "xtal_pool": self.BASIC_PATH.xtal_pool
        }

    def get(self, pool: str, user: object, times: int) -> BASIC_VIEW:
        return self.drivers.get(pool, None)(user, times)