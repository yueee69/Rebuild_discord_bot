import time
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple, Union

from core import constants
from .sqlite_utils import SingletonSQLiteManager

@dataclass
class User:
    user_id: str

    _coin: int = 0
    _fortune: int = 0
    _total_gain: int = 0
    _level: int = 0
    _chat_today: int = 0
    _voice_today: int = 0
    _stream_today: int = 0
    updated_at: int = 0

    manager: object = None
    _dirty: bool = False

    @classmethod
    def new(cls, user_id: str, manager=None) -> "User":
        return cls(
            user_id=str(user_id),
            updated_at=int(time.time()),
            manager=manager
        )

    @classmethod
    def from_row(cls, row: tuple, manager=None) -> "User":
        return cls(
            user_id=row[0],
            _coin=row[1],
            _fortune=row[2],
            _total_gain=row[3],
            _level=row[4],
            _chat_today=row[5],
            _voice_today=row[6],
            _stream_today=row[7],
            updated_at=row[8],
            manager=manager
        )

    # ---------- internal ----------

    def _mark_dirty(self):
        self._dirty = True
        self.updated_at = int(time.time())
        if self.manager:
            self.manager.on_state_dirty(self)

    # ---------- properties (legacy API) ----------

    @property
    def coin(self) -> int:
        return self._coin

    @coin.setter
    def coin(self, value: int):
        value = int(value)
        if value > self._coin:
            gained = value - self._coin
            self._total_gain += gained
            self._level = self._total_gain // constants.USER_LEVEL_COIN_UNIT

        self._coin = value
        self._mark_dirty()

    def add_coin(self, amount: int):
        amount = int(amount)
        if amount == 0:
            return

        self._coin += amount
        self._total_gain += amount
        self._level = int(self._total_gain / constants.USER_LEVEL_COIN_UNIT)
        self._mark_dirty()

    def add_chat_coin(self, amount: int):
        amount = int(amount)
        if amount == 0:
            return

        self._chat_today += amount
        self.add_coin(amount)

    def add_voice_coin(self, amount: int):
        amount = int(amount)
        if amount <= 0:
            return

        self._voice_today += amount
        self.add_coin(amount)

    def add_stream_coin(self, amount: int):
        amount = int(amount)
        if amount <= 0:
            return

        self._stream_today += amount
        self.add_coin(amount)

    def reset_daily_activity(self):
        self._chat_today = 0
        self._voice_today = 0
        self._stream_today = 0
        self._mark_dirty()

    @property
    def fortune(self) -> int:
        return self._fortune

    @fortune.setter
    def fortune(self, value: int):
        value = int(value)
        if value < 0:
            return
        self._fortune = value
        self._mark_dirty()

    @property
    def gain(self) -> int:
        return self._total_gain

    @property
    def level(self) -> int:
        return self._level

    @property
    def chat(self) -> int:
        return self._chat_today

    @property
    def voice(self) -> int:
        return self._voice_today

    @property
    def stream(self) -> int:
        return self._stream_today
    
class UserManager(SingletonSQLiteManager):
    DB_NAME = "user.db"
    DB_PATH = "database/user.db"

    def __init__(self, debug: bool = False):
        if not self._init_sqlite_manager(debug):
            return

        self._states: dict[str, User] = {}
        self._dirty_states: set[str] = set()

        self._init_schema()

    def _init_schema(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS account_state (
            user_id TEXT PRIMARY KEY,
            coin INTEGER NOT NULL DEFAULT 0,
            fortune INTEGER NOT NULL DEFAULT 0,
            total_gain INTEGER NOT NULL DEFAULT 0,
            level INTEGER NOT NULL DEFAULT 0,
            chat_today INTEGER NOT NULL DEFAULT 0,
            voice_today INTEGER NOT NULL DEFAULT 0,
            stream_today INTEGER NOT NULL DEFAULT 0,
            updated_at INTEGER NOT NULL
        )
        """)
        self._ensure_column("account_state", "chat_today", "INTEGER NOT NULL DEFAULT 0")
        self._ensure_column("account_state", "voice_today", "INTEGER NOT NULL DEFAULT 0")
        self._ensure_column("account_state", "stream_today", "INTEGER NOT NULL DEFAULT 0")
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS account_meta (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """)
        self.conn.commit()

    def _ensure_column(self, table_name: str, column_name: str, definition: str):
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        columns = {row[1] for row in self.cursor.fetchall()}
        if column_name not in columns:
            self.cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}")

    def exists(self, user_id: Union[str, int]) -> bool:
        uid = str(user_id)
        with self._lock:
            self.cursor.execute("SELECT 1 FROM account_state WHERE user_id = ? LIMIT 1", (uid,))
            return self.cursor.fetchone() is not None

    def get(self, user_id: Union[str, int], *, create_if_missing: bool = True) -> Optional[User]:
        uid = str(user_id)
        if uid in self._states:
            return self._states[uid]

        with self._lock:
            self.cursor.execute("""
                SELECT user_id, coin, fortune, total_gain, level,
                       chat_today, voice_today, stream_today, updated_at
                FROM account_state
                WHERE user_id = ?
            """, (uid,))
            row = self.cursor.fetchone()

            if row:
                state = User.from_row(row, manager=self)
            else:
                if not create_if_missing:
                    return None
                state = User.new(uid, manager=self)
                self.insert(state)

            self._states[uid] = state
            return state

    def on_state_dirty(self, state: User):
        with self._lock:
            self._dirty_states.add(state.user_id)
            self.flush()

    def insert(self, state: User):
        with self._lock:
            self.cursor.execute("""
            INSERT OR REPLACE INTO account_state (
                user_id, coin, fortune, total_gain, level,
                chat_today, voice_today, stream_today, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                state.user_id,
                state.coin,
                state.fortune,
                state.gain,
                state.level,
                state.chat,
                state.voice,
                state.stream,
                state.updated_at
            ))
            self.conn.commit()

    def flush(self):
        with self._lock:
            if not self._dirty_states:
                return

            for user_id in list(self._dirty_states):
                state = self._states.get(user_id)
                if not state:
                    self._dirty_states.discard(user_id)
                    continue

                self.cursor.execute("""
                UPDATE account_state
                SET coin = ?,
                    fortune = ?,
                    total_gain = ?,
                    level = ?,
                    chat_today = ?,
                    voice_today = ?,
                    stream_today = ?,
                    updated_at = ?
                WHERE user_id = ?
                """, (
                    state.coin,
                    state.fortune,
                    state.gain,
                    state.level,
                    state.chat,
                    state.voice,
                    state.stream,
                    state.updated_at,
                    state.user_id
                ))

                self._dirty_states.discard(user_id)

            self.conn.commit()

    def update(self):
        self.flush()

    def save_all_users(self):
        self.flush()

    def load_all_users(self):
        with self._lock:
            self.cursor.execute("""
                SELECT user_id, coin, fortune, total_gain, level,
                       chat_today, voice_today, stream_today, updated_at
                FROM account_state
            """)
            for row in self.cursor.fetchall():
                state = User.from_row(row, manager=self)
                self._states[state.user_id] = state

    def add_chat_coin(self, user_id: Union[str, int], amount: int) -> bool:
        user = self.get(user_id, create_if_missing=False)
        if not user:
            return False
        user.add_chat_coin(amount)
        return True

    def add_voice_coin(self, user_id: Union[str, int], amount: int) -> bool:
        user = self.get(user_id, create_if_missing=False)
        if not user:
            return False
        user.add_voice_coin(amount)
        return True

    def add_stream_coin(self, user_id: Union[str, int], amount: int) -> bool:
        user = self.get(user_id, create_if_missing=False)
        if not user:
            return False
        user.add_stream_coin(amount)
        return True

    def reset_daily_activity_if_needed(self) -> bool:
        today = self.today_key()
        with self._lock:
            self.cursor.execute("SELECT value FROM account_meta WHERE key = ?", ("daily_activity_date",))
            row = self.cursor.fetchone()
            if row and row[0] == today:
                return False

            self.load_all_users()
            for state in self._states.values():
                state.reset_daily_activity()

            self.cursor.execute(
                "INSERT OR REPLACE INTO account_meta (key, value) VALUES (?, ?)",
                ("daily_activity_date", today)
            )
            self.conn.commit()
            return True

    @staticmethod
    def today_key() -> str:
        tz = timezone(timedelta(hours=constants.TIME_ZONE))
        return datetime.now(tz).date().isoformat()

    def get_meta(self, key: str) -> Optional[str]:
        with self._lock:
            self.cursor.execute("SELECT value FROM account_meta WHERE key = ?", (key,))
            row = self.cursor.fetchone()
            return row[0] if row else None

    def set_meta(self, key: str, value: str):
        with self._lock:
            self.cursor.execute(
                "INSERT OR REPLACE INTO account_meta (key, value) VALUES (?, ?)",
                (key, value)
            )
            self.conn.commit()

    @property
    def UserDatas(self):
        self.load_all_users()
        return self._states

    def get_user(self, userID: Union[str, int], from_register: bool = False) -> Tuple[Optional[User], str]:
        uid = str(userID)

        if self.exists(uid):
            return self.get(uid, create_if_missing=True), "Found"

        if from_register:
            user = self.get(uid, create_if_missing=True)
            self.flush()
            return user, "NotFound"

        return None, "NotFoundAndNeedToRegister"

    def close(self):
        with self._lock:
            if self._closed:
                return
            try:
                self.flush()
                self.conn.close()
            finally:
                self._closed = True
                self.conn = None
