from dataclasses import dataclass
from typing import Union

import random
import time

from .sqlite_utils import SingletonSQLiteManager

@dataclass
class Item_data:
    manager = None
    tool = None

    trans_card: int = 0
    nick_card: int = 0
    role_card: int = 0
    add_role_card: int = 0
    protect: bool = False
    lottery: bool = False

    def __init__(self, ItemJson, manager = None):
        self.manager = manager
        self.tool = ItemTools(self)

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
        self._trans_card = max(value, 0)
        
        if self._trans_card == 0:
            self._protect = False
        self.manager.update()

    @property
    def nick_card(self):
        return self._nick_card

    @nick_card.setter
    def nick_card(self, value: int):
        self._nick_card = max(value, 0)
        self.manager.update()

    @property
    def role_card(self):
        return self._role_card

    @role_card.setter
    def role_card(self, value: int):
        self._role_card = max(value, 0)
        self.manager.update()

    @property
    def add_role_card(self):
        return self._add_role_card

    @add_role_card.setter
    def add_role_card(self, value: int):
        self._add_role_card = max(value, 0)
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

    def to_dict(self):
        return {
        "trans": self._trans_card,
        "nick": self._nick_card,
        "role": self._role_card,
        "add_role": self._add_role_card,
        "protect": self._protect,
        "lottery": self._lottery
    }

class ItemManager(SingletonSQLiteManager):
    DB_NAME = "item.db"

    def __init__(self, debug=False):
        if not self._init_sqlite_manager(debug):
            return

        self.ItemDatas = {} # {userID: itemData}
        self._init_schema()
        if not self.debug:
            self.load_all_users()

    def _init_schema(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS item_state (
            user_id TEXT PRIMARY KEY,
            trans INTEGER NOT NULL DEFAULT 0,
            nick INTEGER NOT NULL DEFAULT 0,
            role INTEGER NOT NULL DEFAULT 0,
            add_role INTEGER NOT NULL DEFAULT 0,
            protect INTEGER NOT NULL DEFAULT 0,
            lottery INTEGER NOT NULL DEFAULT 0,
            updated_at INTEGER NOT NULL
        )
        """)
        self.conn.commit()

    def load_all_users(self):
        self.ItemDatas.clear()
        self.cursor.execute("""
            SELECT user_id, trans, nick, role, add_role, protect, lottery
            FROM item_state
        """)
        for user_id, trans, nick, role, add_role, protect, lottery in self.cursor.fetchall():
            user = Item_data({
                "trans": trans,
                "nick": nick,
                "role": role,
                "add_role": add_role,
                "protect": bool(protect),
                "lottery": bool(lottery)
            }, manager=self)
            self.__add_user(user, user_id)
        self._remember_database_signature()

    def reload_from_database(self):
        self.load_all_users()
            
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
        self._reload_if_database_changed()
        user = self.ItemDatas.get(str(userID)) 
        if not user:
            instance = self.__create_user_instance()
            user = self.__add_user(instance, userID)
            self.save_all_users()
        return user
    
    def save_all_users(self):
        now = int(time.time())
        for userID, value in self.ItemDatas.items():
            data = value.to_dict()
            self.cursor.execute("""
            INSERT OR REPLACE INTO item_state
            (user_id, trans, nick, role, add_role, protect, lottery, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(userID),
                int(data["trans"]),
                int(data["nick"]),
                int(data["role"]),
                int(data["add_role"]),
                int(bool(data["protect"])),
                int(bool(data["lottery"])),
                now
            ))
        self.conn.commit()
        self._remember_database_signature()

    def reset_daily_lottery_flags(self):
        with self._lock:
            self.load_all_users()
            for item in self.ItemDatas.values():
                item._lottery = False

            self.cursor.execute(
                "UPDATE item_state SET lottery = 0, updated_at = ?",
                (int(time.time()),)
            )
            self.conn.commit()
            self._remember_database_signature()


class ItemTools:
    ITEM_POOLS_TRANS = {
            "迴轉卡": "trans_card",
            "增加身分組卡": "add_role_card",
            "指定身分組卡": "role_card",
            "指定暱稱卡": "nick_card"
        }
    
    def __init__(self, item: Item_data):
        self.item = item

    def dump_items(self, prize: str):
        if prize in self.ITEM_POOLS_TRANS:
            attr_name = self.ITEM_POOLS_TRANS[prize]
            setattr(self.item, attr_name, getattr(self.item, attr_name) + 1)

    def random_card(self) -> str:
        """隨機抽一張卡片，返回一個名稱"""
        card = random.choice(list(self.ITEM_POOLS_TRANS.keys()))
        return self.ITEM_POOLS_TRANS.get(card), card
