import random
import sqlite3
import time
from dataclasses import dataclass

from .sqlite_utils import SingletonSQLiteManager

DISABLED_VISIBLE_ITEM_KEYWORDS = ("RPG金幣", "RPG 金幣")


def is_visible_shop_item(item_name: str) -> bool:
    return not any(keyword in item_name for keyword in DISABLED_VISIBLE_ITEM_KEYWORDS)

class DailyShopData:
    def __init__(self, goods: dict, manager=None, row_id: int = None):
        self.manager = manager
        self.row_id = row_id
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
        if self.manager:
            self.manager.update()

    def to_dict(self):
        return {
            "item": self._item,
            "price": self._price,
            "left_count": self._left_count
        }

class DailyShopManager(SingletonSQLiteManager):
    DB_NAME = "daily_shop.db"
    shop_data: list[DailyShopData]

    def __init__(self, debug = False):
        if not self._init_sqlite_manager(debug):
            return

        self.shop_data = [] 
        self._init_schema()
        if not self.debug:
            self.load_all_goods()

    def _init_schema(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_shop_goods (
            position INTEGER PRIMARY KEY,
            item TEXT NOT NULL,
            price INTEGER NOT NULL,
            left_count INTEGER NOT NULL,
            updated_at INTEGER NOT NULL
        )
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_shop_purchases (
            user_id TEXT NOT NULL,
            shop_date TEXT NOT NULL,
            item_position INTEGER NOT NULL,
            item TEXT NOT NULL,
            purchased_at INTEGER NOT NULL,
            PRIMARY KEY (user_id, shop_date)
        )
        """)
        self.conn.commit()

    def load_all_goods(self):
        self.shop_data.clear()
        self.cursor.execute("""
            SELECT position, item, price, left_count
            FROM daily_shop_goods
            ORDER BY position
        """)
        for position, item, price, left_count in self.cursor.fetchall():
            if not is_visible_shop_item(item):
                continue
            self.shop_data.append(
                DailyShopData({
                    "item": item,
                    "price": price,
                    "left_count": left_count
                }, manager=self, row_id=position)
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
        for idx, item in enumerate(items):
            self.shop_data.append(DailyShopData(item.generate_data(), manager=self, row_id=idx))
        self.update()

    def update(self):
        if self.debug:
            print("update function is called")
        else:
            self.save_all_goods()
            print("(daily_shop_manager) save all users success")

    @staticmethod
    def today_key() -> str:
        return time.strftime("%Y-%m-%d", time.localtime())

    def user_has_purchased_today(self, user_id: str | int) -> bool:
        with self._lock:
            self.cursor.execute("""
                SELECT 1
                FROM daily_shop_purchases
                WHERE user_id = ? AND shop_date = ?
                LIMIT 1
            """, (str(user_id), self.today_key()))
            return self.cursor.fetchone() is not None

    def reserve_daily_purchase(self, user_id: str | int, position: int) -> str:
        """
        Reserves a daily-shop purchase before reward delivery.
        Returns: ok, already_purchased, sold_out, not_found
        """
        uid = str(user_id)
        today = self.today_key()
        now = int(time.time())

        with self._lock:
            self.cursor.execute("""
                SELECT item, left_count
                FROM daily_shop_goods
                WHERE position = ?
            """, (int(position),))
            row = self.cursor.fetchone()
            if not row:
                return "not_found"

            item_name, left_count = row
            if int(left_count) <= 0:
                return "sold_out"

            try:
                self.cursor.execute("""
                    INSERT INTO daily_shop_purchases
                    (user_id, shop_date, item_position, item, purchased_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (uid, today, int(position), item_name, now))
            except sqlite3.IntegrityError:
                self.conn.rollback()
                return "already_purchased"

            self.cursor.execute("""
                UPDATE daily_shop_goods
                SET left_count = left_count - 1,
                    updated_at = ?
                WHERE position = ? AND left_count > 0
            """, (now, int(position)))

            if self.cursor.rowcount != 1:
                self.conn.rollback()
                return "sold_out"

            self.conn.commit()

        for goods in self.shop_data:
            if goods.row_id == int(position):
                goods._left_count = max(goods.left_count - 1, 0)
                break

        return "ok"

    def save_all_goods(self):
        now = int(time.time())
        self.cursor.execute("DELETE FROM daily_shop_goods")
        for idx, goods in enumerate(self.shop_data):
            if not is_visible_shop_item(goods.item):
                continue
            goods.manager = self
            goods.row_id = idx
            data = goods.to_dict()
            self.cursor.execute("""
            INSERT OR REPLACE INTO daily_shop_goods (position, item, price, left_count, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """, (
                idx,
                data["item"],
                int(data["price"]),
                int(data["left_count"]),
                now
            ))
        self.conn.commit()


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
