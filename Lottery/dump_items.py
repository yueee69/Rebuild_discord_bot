from abc import ABC, abstractmethod

from managers.air_manager import AirManager
from managers.item_manager import ItemManager
from managers.history_manager import HistoryManager

class Dump_items(ABC):
    @abstractmethod
    def dump_items():
        pass

class Norm_pool(Dump_items):
    def dump_items(self, prizes: list, userData: object):
        HistoryManager().append_items(userData.user_id, prizes, pool="norm_pool")
        air_count = 0
        for item in prizes:
            prize = getattr(item, "prize", item)
            if prize.startswith('鮭魚幣'):
                coin = int(prize.split('鮭魚幣+')[1])
                userData.coin += coin
            elif prize == "空氣":
                air_count += 1

        if air_count:
            air_data = AirManager().get_user(userData.user_id)
            air_data.times += air_count

class Item_pool(Dump_items):
    """
    這裡先寫邏輯，後續再改成策略/工廠模式
    """
    def dump_items(self, prizes: list, userData: object):
        HistoryManager().append_items(userData.user_id, prizes, pool="item_pool")
        itemData = ItemManager().get_user(userData.user_id)
        item_pools_trans ={
        "迴轉卡":"trans",
        "增加身分組卡":"add_role",
        "指定身分組卡":"role",
        "指定暱稱卡":"nick"    
        }
        for item in prizes:
            prize = getattr(item, "prize", item)
            if prize.startswith('鮭魚幣'):
                coin = int(prize.split('鮭魚幣+')[1])
                userData.coin += coin

            elif prize in list(item_pools_trans):
                itemData.tool.dump_items(prize)

class Xtal_pool(Dump_items):
    def dump_items(self, prizes: list, userData: object):
        pass #先不做
