import random
from dataclasses import dataclass

from utils.general import Toolkit

class DailyShopData:
    def __init__(self, goods: dict):
        self._item: str = goods["item"]
        self._price: int = goods["price"]
        self._left_count: int = goods["left_count"]

    @property
    def item(self):
        return self._item
    
    @property
    def price(self):
        return self._price
    
    @property
    def left_count(self):
        return self._left_count
    
    @left_count.setter
    def left_count(self, value: int):
        self._left_count = value

    def to_dict(self):
        return {
            "item": self._item,
            "price": self._price,
            "left_count": self._left_count
        }

class DailyShopManager:
    shop_data: list[DailyShopData]

    def __init__(self, debug = False):
        self.shop_data = [] 
        self.debug = debug
        if self.debug:
            print("\DailyShopManager in debug mode")
        else:
            self.load_all_goods()

    def load_all_goods(self):
        data = Toolkit.open_jsons("daily_shop.json")
        for goods in data:
            self.shop_data.append(
                DailyShopData(goods)
            )

    def get_goods(self, *index: int):
        """
        如果提供了 index，就只取對應商品，否則回傳全部
        """
        if not index:
            return self.shop_data
        
        return [self.shop_data[i] for i in index]
    
    def daily_random_goods(self):
        items = DailyShopModel().random_goods()
        self.shop_data = []
        for item in items:
            self.shop_data.append(DailyShopData(item.generate_data()))
        self.update()

    def update(self):
        if self.debug:
            print("update function is called")
        else:
            self.save_all_goods()
            print("(daily_shop_manager) save all users success")

    def save_all_goods(self):
        instances = []
        for goods in self.shop_data:
            instances.append(
                goods.to_dict()
            )
        Toolkit.dump_jsons(("daily_shop.json", instances))


@dataclass
class DailyShopItem:
    name: str
    price: int
    discount_percent: int
    weight: int

    def generate_data(self) -> dict:
        return {
            "item": self.name,
            "price": self.discounted_price,
            "left_count": random.randint(1, 7)
        }

    @property
    def discounted_price(self) -> int:
        return int(self.price * self.discount_percent / 100)


class DailyShopModel:
    def __init__(self):
        self.shop_pool: list[DailyShopItem] = self._load_default_items()

    def _load_default_items(self):
        return [
            DailyShopItem("3陽壽", 10500, 35, 42),
            DailyShopItem("5陽壽", 17500, 35, 18),
            DailyShopItem("7陽壽", 24500, 40, 12),
            DailyShopItem("10陽壽", 35000, 50, 5),
            DailyShopItem("5萬眾神幣", 5000, 5, 10),
            DailyShopItem("10萬眾神幣", 10000, 10, 5),
            DailyShopItem("50萬眾神幣", 45000, 100, 5),
            DailyShopItem("100萬眾神幣", 60000, 100, 1),
            DailyShopItem("舞者之書", 80000, 50, 1),
            DailyShopItem("魔法戰士之書", 70000, 50, 1),
        ]

    def random_goods(self, count: int = 3) -> list[DailyShopItem]:
        return random.choices(self.shop_pool, weights = [item.weight for item in self.shop_pool], k = count)