import json
import time
from dataclasses import dataclass, field
from typing import List, Union

from .sqlite_utils import SingletonSQLiteManager


@dataclass
class HistoryData:
    manager: object = None
    user_lottery_history_list: List = field(default_factory=list)

    def __init__(self, LotteryHistoryJson, manager=None):
        self.manager = manager
        self.user_lottery_history_list = LotteryHistoryJson

    def get_items(self):
        result = []
        for item in self.user_lottery_history_list:
            result.append({
                "item": item["prize"],
                "time": item["time"]
            })
        return result

    def dump_items(self, items: Union[str, list]):
        if isinstance(items, list):
            self.user_lottery_history_list.extend(items)
        elif isinstance(items, str):
            self.user_lottery_history_list.append(items)

        if self.manager:
            self.manager.update()

    def to_dict(self):
        return self.user_lottery_history_list


class HistoryManager(SingletonSQLiteManager):
    DB_NAME = "history.db"

    def __init__(self, debug=False):
        if not self._init_sqlite_manager(debug):
            return

        self.HistoryDatas = {}
        self._init_schema()
        if not self.debug:
            self.load_all_users()

    def _init_schema(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS lottery_history (
            user_id TEXT PRIMARY KEY,
            history_json TEXT NOT NULL,
            updated_at INTEGER NOT NULL
        )
        """)
        self.conn.commit()

    def load_all_users(self):
        self.HistoryDatas.clear()
        self.cursor.execute("SELECT user_id, history_json FROM lottery_history")
        for user_id, history_json in self.cursor.fetchall():
            user = HistoryData(json.loads(history_json), manager=self)
            self.__add_user(user, user_id)

    def update(self):
        if self.debug:
            print("update function is called")
        else:
            self.save_all_users()
            print("(history_manager) save all users success")

    def __add_user(self, HistoryData: HistoryData, userID: Union[str, int]) -> HistoryData:
        HistoryData.manager = self
        self.HistoryDatas[str(userID)] = HistoryData
        return HistoryData

    def __create_user_instance(self) -> HistoryData:
        return HistoryData([], manager=self)

    def get_user(self, userID: Union[str, int]) -> HistoryData:
        user = self.HistoryDatas.get(str(userID))
        if not user:
            instance = self.__create_user_instance()
            user = self.__add_user(instance, userID)
            self.save_all_users()
        return user

    def save_all_users(self):
        now = int(time.time())
        for userID, value in self.HistoryDatas.items():
            self.cursor.execute("""
            INSERT OR REPLACE INTO lottery_history (user_id, history_json, updated_at)
            VALUES (?, ?, ?)
            """, (
                str(userID),
                json.dumps(value.to_dict(), ensure_ascii=False),
                now
            ))
        self.conn.commit()
