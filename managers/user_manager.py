import time
from dataclasses import dataclass
from typing import Optional, Tuple, Union

from .sqlite_utils import SingletonSQLiteManager

@dataclass
class User:
    user_id: str

    _coin: int = 0
    _fortune: int = 0
    _total_gain: int = 0
    _level: int = 0
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
            updated_at=row[5],
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
            self._level = self._total_gain // 1500

        self._coin = value
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
            updated_at INTEGER NOT NULL
        )
        """)
        self.conn.commit()

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
                SELECT user_id, coin, fortune, total_gain, level, updated_at
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
            INSERT OR REPLACE INTO account_state (user_id, coin, fortune, total_gain, level, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                state.user_id,
                state.coin,
                state.fortune,
                state.gain,
                state.level,
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
                    updated_at = ?
                WHERE user_id = ?
                """, (
                    state.coin,
                    state.fortune,
                    state.gain,
                    state.level,
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
                SELECT user_id, coin, fortune, total_gain, level, updated_at
                FROM account_state
            """)
            for row in self.cursor.fetchall():
                state = User.from_row(row, manager=self)
                self._states[state.user_id] = state

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
