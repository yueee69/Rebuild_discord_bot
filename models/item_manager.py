from dataclasses import dataclass
from typing import Union

import random

from new_bot.utils.general import Toolkit

@dataclass
class Item_data:
    manager = None
    trans_card: int = 0
    nick_card: int = 0
    role_card: int = 0
    add_role_card: int = 0
    protect: bool = False
    lottery: bool = False
    
    item_pools_trans = {
            "迴轉卡": "trans_card",
            "增加身分組卡": "add_role_card",
            "指定身分組卡": "role_card",
            "指定暱稱卡": "nick_card"
        }

    def __init__(self, ItemJson, manager=None):
        self.manager = manager
        self._trans_card = ItemJson["trans"]
        self._nick_card = ItemJson["nick"]
        self._role_card = ItemJson["role"]
        self._add_role_card = ItemJson["add_role"]
        self._protect = ItemJson["protect"]
        self._lottery = ItemJson["lottery"]

    @property
    def trans_card(self):
        return self._trans_card

    @trans_card.setter
    def trans_card(self, value: int):
        self._trans_card = value
        if self._trans_card == 0:
            self._protect = False
        self.manager.update()

    @property
    def nick_card(self):
        return self._nick_card

    @nick_card.setter
    def nick_card(self, value: int):
        self._nick_card = value
        self.manager.update()

    @property
    def role_card(self):
        return self._role_card

    @role_card.setter
    def role_card(self, value: int):
        self._role_card = value
        self.manager.update()

    @property
    def add_role_card(self):
        return self._add_role_card

    @add_role_card.setter
    def add_role_card(self, value: int):
        self._add_role_card = value
        self.manager.update()

    @property
    def protect(self):
        return self._protect

    @protect.setter
    def protect(self, value: bool):
        self._protect = value
        self.manager.update()

    @property
    def lottery(self):
        return self._lottery

    @lottery.setter
    def lottery(self, value: bool):
        self._lottery = value
        self.manager.update()

    def dump_items(self, prize: str):
        if prize in self.item_pools_trans:
            attr_name = self.item_pools_trans[prize]
            setattr(self, attr_name, getattr(self, attr_name) + 1)
            self.manager.update()

    def random_card(self) -> str:
        """隨機抽一張卡片，返回一個名稱"""
        card = random.choice(list(self.item_pools_trans.keys()))
        return self.item_pools_trans.get(card), card

    def to_dict(self):
        return {
        "trans": self._trans_card,
        "nick": self._nick_card,
        "role": self._role_card,
        "add_role": self._add_role_card,
        "protect": self._protect,
        "lottery": self._lottery
    }

class ItemManager:
    def __init__(self, debug=False):
        self.ItemDatas = {} # {userID: itemData}
        self.debug = debug
        if self.debug:
            print("\nUserManager in debug mode")
        elif not self.debug:
            self.load_all_users()
    
    def load_all_users(self):
        data = Toolkit.open_jsons("item.json")
        for user_id, user_info in data.items():
            #print(f"Loading user {user_id}: {user_info}") 
            user = Item_data(user_info, manager=self)
            self.__add_user(user, user_id)
            
    def update(self):
        if self.debug:
            print("update function is called")
        elif not self.debug:
            self.save_all_users()
            print("(item_manager) save all users success")
        
    # 禁止直接新增 User ，請使用 get_user 獲取用戶後再進行操作
    def __add_user(self, itemData: Item_data, userID: Union[str, int]) -> Item_data:
        itemData.manager = self
        self.ItemDatas[str(userID)] = itemData
        return itemData

    def __create_user_instance(self) -> Item_data:
        new_data = {"trans": 0, "nick": 0, "role": 0, "add_role": 0,"protect":False,"lottery":False}
        return Item_data(new_data, manager=self)

    def get_user(self, userID: Union[str, int]) -> Item_data:
        user = self.ItemDatas.get(str(userID)) 
        if not user:
            instance = self.__create_user_instance()
            user = self.__add_user(instance, userID)
            self.save_all_users()
        return user
    
    def save_all_users(self):
        json_data = {userID: value.to_dict() for userID, value in self.ItemDatas.items()}
        Toolkit.dump_jsons(("item.json", json_data))