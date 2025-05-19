from abc import ABC, abstractmethod

from models.item_manager import ItemManager

class Dump_items(ABC):
    @abstractmethod
    def dump_items():
        pass

class Norm_pool(Dump_items):
    def dump_items(self, prizes: list, userData: object):
        for item in prizes:
            if item.startswith('鮭魚幣'):
                coin = int(item.split('鮭魚幣+')[1])
                userData.coin += coin

class Item_pool(Dump_items):
    """
    這裡先寫邏輯，後續再改成策略/工廠模式
    """
    def dump_items(self, prizes: list, userData: object):
        itemData = ItemManager().get_user(userData.user_id)
        item_pools_trans ={
        "迴轉卡":"trans",
        "增加身分組卡":"add_role",
        "指定身分組卡":"role",
        "指定暱稱卡":"nick"    
        }
        for item in prizes:
            if item.startswith('鮭魚幣'):
                coin = int(item.split('鮭魚幣+')[1])
                userData.coin += coin

            elif item in list(item_pools_trans):
                itemData.tool.dump_items(item)

class Xtal_pool(Dump_items):
    def dump_items(self, prizes: list, userData: object):
        pass #先不做