import time
from dataclasses import dataclass
from typing import Union

from .sqlite_utils import SingletonSQLiteManager


@dataclass
class Air_Data:
    manager = None
    times: int = 0

    def __init__(self, AirJson, manager=None):
        self.manager = manager
        self._times = AirJson["times"]

    @property
    def times(self):
        return self._times

    @times.setter
    def times(self, value):
        self._times = value
        self.manager.update()

    def to_dict(self):
        return {
            "times": self._times
        }


class AirManager(SingletonSQLiteManager):
    DB_NAME = "air.db"

    def __init__(self, debug=False):
        if not self._init_sqlite_manager(debug):
            return

        self.AirDatas = {}
        self._init_schema()
        if not self.debug:
            self.load_all_users()

    def _init_schema(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS air_state (
            user_id TEXT PRIMARY KEY,
            times INTEGER NOT NULL DEFAULT 0,
            updated_at INTEGER NOT NULL
        )
        """)
        self.conn.commit()

    def load_all_users(self):
        self.AirDatas.clear()
        self.cursor.execute("SELECT user_id, times FROM air_state")
        for user_id, times in self.cursor.fetchall():
            user = Air_Data({"times": times}, manager=self)
            self.__add_user(user, user_id)

    def update(self):
        if self.debug:
            print("update function is called")
        else:
            self.save_all_users()
            print("(air_manager) save all users success")

    def __add_user(self, AirData: Air_Data, userID: Union[str, int]) -> Air_Data:
        AirData.manager = self
        self.AirDatas[str(userID)] = AirData
        return AirData

    def __create_user_instance(self) -> Air_Data:
        return Air_Data({"times": 0}, manager=self)

    def get_user(self, userID: Union[str, int]) -> Air_Data:
        user = self.AirDatas.get(str(userID))
        if not user:
            instance = self.__create_user_instance()
            user = self.__add_user(instance, userID)
            self.save_all_users()
        return user

    def save_all_users(self):
        now = int(time.time())
        for userID, value in self.AirDatas.items():
            self.cursor.execute("""
            INSERT OR REPLACE INTO air_state (user_id, times, updated_at)
            VALUES (?, ?, ?)
            """, (
                str(userID),
                int(value.times),
                now
            ))
        self.conn.commit()
