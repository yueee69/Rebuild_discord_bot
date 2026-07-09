import json
import re
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable, Union

from core import constants
from .sqlite_utils import SingletonSQLiteManager


VALID_POOLS = {"norm_pool", "item_pool"}
POOL_DISPLAY_NAMES = {
    "norm_pool": "一般抽獎",
    "item_pool": "每日道具抽獎",
}


@dataclass
class HistoryEntry:
    entry_id: int
    user_id: str
    user_entry_id: int
    prize: str
    pool: str
    rarity: str
    pity_before: int | None
    pity_after: int | None
    is_pity_reset: bool
    display_time: str
    created_at: int

    @property
    def display_text(self) -> str:
        pool_name = POOL_DISPLAY_NAMES.get(self.pool, self.pool)
        details = [self.display_time, f"獎池: {pool_name}"]
        return "\n".join(details)


class HistoryData:
    def __init__(self, user_id: Union[str, int], manager: "HistoryManager"):
        self.user_id = str(user_id)
        self.manager = manager

    def get_items(self):
        return [
            {
                "item": entry.prize,
                "time": entry.display_text,
            }
            for entry in self.manager.get_entries(self.user_id)
        ]

    def dump_items(self, items: Union[str, list], pool: str = "norm_pool"):
        self.manager.append_items(self.user_id, items, pool=pool)


class HistoryManager(SingletonSQLiteManager):
    DB_NAME = "history.db"
    MIGRATION_KEY = "json_to_entries_v2"

    def __init__(self, debug=False):
        if not self._init_sqlite_manager(debug):
            return

        self._cache: dict[str, HistoryData] = {}
        self._init_schema()
        self._upgrade_entries_table()
        self._migrate_legacy_history()
        self._drop_legacy_table()

    def _init_schema(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS lottery_history_entries (
            id INTEGER PRIMARY KEY,
            user_id TEXT NOT NULL,
            user_entry_id INTEGER NOT NULL DEFAULT 0,
            prize TEXT NOT NULL,
            pool TEXT NOT NULL DEFAULT 'norm_pool' CHECK (pool IN ('norm_pool', 'item_pool')),
            rarity TEXT NOT NULL DEFAULT '',
            pity_before INTEGER,
            pity_after INTEGER,
            is_pity_reset INTEGER NOT NULL DEFAULT 0,
            display_time TEXT NOT NULL,
            created_at INTEGER NOT NULL,
            UNIQUE(user_id, user_entry_id)
        )
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS history_meta (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """)
        self.conn.commit()
        self._ensure_indexes()
        self._remember_database_signature()

    def _migrate_legacy_history(self):
        if self._get_meta(self.MIGRATION_KEY) == "done":
            return
        if not self._table_exists("lottery_history"):
            self._set_meta(self.MIGRATION_KEY, "done")
            self.conn.commit()
            return
        if self._entries_count() > 0 and self._get_meta("json_to_entries_v1") == "done":
            self._set_meta(self.MIGRATION_KEY, "done")
            self.conn.commit()
            return

        self.cursor.execute("SELECT user_id, history_json, updated_at FROM lottery_history")
        rows = self.cursor.fetchall()
        for user_id, history_json, updated_at in rows:
            try:
                items = json.loads(history_json)
            except (TypeError, json.JSONDecodeError):
                continue

            if not isinstance(items, list):
                continue

            for index, item in enumerate(items):
                if not isinstance(item, dict):
                    continue

                created_at = int(updated_at or time.time()) + index
                prize = str(item.get("prize", "未知獎品"))
                display_time = self.normalize_display_time(item.get("time"), created_at)
                self.cursor.execute("""
                    INSERT INTO lottery_history_entries
                    (user_id, user_entry_id, prize, pool, rarity, pity_before, pity_after, is_pity_reset, display_time, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(user_id, user_entry_id) DO NOTHING
                """, (
                    str(user_id),
                    index + 1,
                    prize,
                    "norm_pool",
                    "",
                    None,
                    None,
                    0,
                    display_time,
                    created_at,
                ))

        self._set_meta(self.MIGRATION_KEY, "done")
        self.conn.commit()
        self._remember_database_signature()

    def _upgrade_entries_table(self):
        if not self._table_exists("lottery_history_entries"):
            return

        self.cursor.execute("PRAGMA table_info(lottery_history_entries)")
        columns = {row[1] for row in self.cursor.fetchall()}
        self.cursor.execute("""
            SELECT sql
            FROM sqlite_master
            WHERE type = 'table' AND name = 'lottery_history_entries'
        """)
        row = self.cursor.fetchone()
        table_sql = row[0] if row else ""
        required_columns = {"user_entry_id", "rarity", "pity_before", "pity_after", "is_pity_reset"}
        needs_rebuild = (
            not required_columns.issubset(columns)
            or "AUTOINCREMENT" in table_sql.upper()
            or "CHECK (pool IN" not in table_sql
        )

        if not needs_rebuild:
            self._normalize_existing_entries()
            return

        self.cursor.execute("SELECT * FROM lottery_history_entries ORDER BY user_id, created_at, id")
        column_names = [description[0] for description in self.cursor.description]
        rows = [
            dict(zip(column_names, row))
            for row in self.cursor.fetchall()
        ]

        self.cursor.execute("DROP TABLE IF EXISTS lottery_history_entries_new")
        self.cursor.execute("""
        CREATE TABLE lottery_history_entries_new (
            id INTEGER PRIMARY KEY,
            user_id TEXT NOT NULL,
            user_entry_id INTEGER NOT NULL,
            prize TEXT NOT NULL,
            pool TEXT NOT NULL DEFAULT 'norm_pool' CHECK (pool IN ('norm_pool', 'item_pool')),
            rarity TEXT NOT NULL DEFAULT '',
            pity_before INTEGER,
            pity_after INTEGER,
            is_pity_reset INTEGER NOT NULL DEFAULT 0,
            display_time TEXT NOT NULL,
            created_at INTEGER NOT NULL,
            UNIQUE(user_id, user_entry_id)
        )
        """)

        user_counts: dict[str, int] = {}
        for row in rows:
            entry_id = row["id"]
            user_id = row["user_id"]
            prize = row["prize"]
            pool = row.get("pool", "norm_pool")
            rarity = row.get("rarity", "")
            pity_before = row.get("pity_before")
            pity_after = row.get("pity_after")
            is_pity_reset = row.get("is_pity_reset", 0)
            display_time = row["display_time"]
            created_at = row["created_at"]
            uid = str(user_id)
            user_counts[uid] = user_counts.get(uid, 0) + 1
            self.cursor.execute("""
                INSERT INTO lottery_history_entries_new
                (id, user_id, user_entry_id, prize, pool, rarity, pity_before, pity_after, is_pity_reset, display_time, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry_id,
                uid,
                user_counts[uid],
                str(prize),
                self.normalize_pool(pool),
                str(rarity or ""),
                pity_before,
                pity_after,
                int(bool(is_pity_reset)),
                self.normalize_display_time(display_time, created_at),
                int(created_at),
            ))

        self.cursor.execute("DROP TABLE lottery_history_entries")
        self.cursor.execute("ALTER TABLE lottery_history_entries_new RENAME TO lottery_history_entries")
        if self._table_exists("sqlite_sequence"):
            self.cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'lottery_history_entries'")
        self.conn.commit()
        self._ensure_indexes()
        self._remember_database_signature()

    def _normalize_existing_entries(self):
        self.cursor.execute("""
            SELECT id, pool, display_time, created_at
            FROM lottery_history_entries
        """)
        rows = self.cursor.fetchall()
        for entry_id, pool, display_time, created_at in rows:
            self.cursor.execute("""
                UPDATE lottery_history_entries
                SET pool = ?,
                    display_time = ?
                WHERE id = ?
            """, (
                self.normalize_pool(pool),
                self.normalize_display_time(display_time, created_at),
                entry_id,
            ))
        self.conn.commit()
        self._remember_database_signature()

    def _drop_legacy_table(self):
        self.cursor.execute("DROP TABLE IF EXISTS lottery_history")
        self.conn.commit()
        self._remember_database_signature()

    def _ensure_indexes(self):
        self.cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_lottery_history_entries_user_created
        ON lottery_history_entries (user_id, created_at DESC, id DESC)
        """)
        self.cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_lottery_history_entries_prize_created
        ON lottery_history_entries (prize, created_at DESC, id DESC)
        """)
        self.conn.commit()

    def get_user(self, userID: Union[str, int]) -> HistoryData:
        self._reload_if_database_changed()
        uid = str(userID)
        if uid not in self._cache:
            self._cache[uid] = HistoryData(uid, self)
        return self._cache[uid]

    def get_entries(self, user_id: Union[str, int], limit: int = 100) -> list[HistoryEntry]:
        self._reload_if_database_changed()
        with self._lock:
            self.cursor.execute("""
                SELECT id,
                       user_id,
                       user_entry_id,
                       prize,
                       pool,
                       rarity,
                       pity_before,
                       pity_after,
                       is_pity_reset,
                       display_time,
                       created_at
                FROM lottery_history_entries
                WHERE user_id = ?
                ORDER BY created_at DESC, id DESC
                LIMIT ?
            """, (str(user_id), int(limit)))
            entries = []
            for row in self.cursor.fetchall():
                entry = HistoryEntry(*row)
                entry.is_pity_reset = bool(entry.is_pity_reset)
                entries.append(entry)
            return entries

    def append_items(self, user_id: Union[str, int], items: Union[str, Iterable[str]], pool: str = "norm_pool"):
        if isinstance(items, str):
            prizes = [items]
        else:
            prizes = list(items)

        uid = str(user_id)
        now = int(time.time())
        display_time = self.format_time(now)
        pool = self.normalize_pool(pool)
        with self._lock:
            next_user_entry_id = self._next_user_entry_id(uid)
            for offset, item in enumerate(prizes):
                prize = getattr(item, "prize", item)
                self.cursor.execute("""
                    INSERT INTO lottery_history_entries
                    (user_id, user_entry_id, prize, pool, rarity, pity_before, pity_after, is_pity_reset, display_time, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    uid,
                    next_user_entry_id + offset,
                    str(prize),
                    pool,
                    str(getattr(item, "rarity", "") or ""),
                    getattr(item, "pity_before", None),
                    getattr(item, "pity_after", None),
                    int(bool(getattr(item, "is_pity_reset", False))),
                    display_time,
                    now + offset,
                ))
            self.conn.commit()
            self._remember_database_signature()

    def _next_user_entry_id(self, user_id: str) -> int:
        self.cursor.execute("""
            SELECT COALESCE(MAX(user_entry_id), 0) + 1
            FROM lottery_history_entries
            WHERE user_id = ?
        """, (user_id,))
        return int(self.cursor.fetchone()[0])

    def load_all_users(self):
        self._cache.clear()
        self.cursor.execute("SELECT DISTINCT user_id FROM lottery_history_entries")
        for (user_id,) in self.cursor.fetchall():
            self._cache[str(user_id)] = HistoryData(user_id, self)
        self._remember_database_signature()

    def reload_from_database(self):
        self.load_all_users()

    def update(self):
        self._remember_database_signature()

    def save_all_users(self):
        self._remember_database_signature()

    def _table_exists(self, table_name: str) -> bool:
        self.cursor.execute("""
            SELECT 1
            FROM sqlite_master
            WHERE type = 'table' AND name = ?
            LIMIT 1
        """, (table_name,))
        return self.cursor.fetchone() is not None

    def _entries_count(self) -> int:
        if not self._table_exists("lottery_history_entries"):
            return 0
        self.cursor.execute("SELECT COUNT(*) FROM lottery_history_entries")
        return int(self.cursor.fetchone()[0])

    def _get_meta(self, key: str) -> str | None:
        self.cursor.execute("SELECT value FROM history_meta WHERE key = ?", (key,))
        row = self.cursor.fetchone()
        return row[0] if row else None

    def _set_meta(self, key: str, value: str):
        self.cursor.execute(
            "INSERT OR REPLACE INTO history_meta (key, value) VALUES (?, ?)",
            (key, value),
        )

    @staticmethod
    def normalize_pool(pool: str | None) -> str:
        return pool if pool in VALID_POOLS else "norm_pool"

    @classmethod
    def normalize_display_time(cls, value: object, fallback_timestamp: int | None = None) -> str:
        numbers = re.findall(r"\d+", str(value or ""))
        if len(numbers) >= 6:
            year, month, day, hour, minute, second = [int(number) for number in numbers[:6]]
            return f"{year} / {month:02d} / {day:02d} | {hour:02d} : {minute:02d} : {second:02d}"
        return cls.format_time(fallback_timestamp)

    @staticmethod
    def format_time(timestamp: int | None = None) -> str:
        tz = timezone(timedelta(hours=constants.TIME_ZONE))
        dt = datetime.fromtimestamp(timestamp or time.time(), tz)
        return f"{dt.year} / {dt.month:02d} / {dt.day:02d} | {dt.hour:02d} : {dt.minute:02d} : {dt.second:02d}"
