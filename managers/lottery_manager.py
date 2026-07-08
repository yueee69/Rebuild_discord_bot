import time
from dataclasses import dataclass

from .sqlite_utils import SingletonSQLiteManager

@dataclass
class LotteryState:
    user_id: str
    _current_lottery_times: int = 0
    _total_lottery_times: int = 0
    _item_pool_is_lottery: bool = False
    _air_times: int = 0
    updated_at: int = 0

    manager: object = None
    _dirty: bool = False

    # ---------- factory ----------

    @classmethod
    def new(cls, user_id: str, manager=None) -> "LotteryState":
        return cls(
            user_id=user_id,
            updated_at=int(time.time()),
            manager=manager
        )

    @classmethod
    def from_row(cls, row: tuple, manager=None) -> "LotteryState":
        return cls(
            user_id=row[0],
            _current_lottery_times=row[1],
            _total_lottery_times=row[2],
            _item_pool_is_lottery=bool(row[3]),
            _air_times=row[4],
            updated_at=row[5],
            manager=manager
        )

    # ---------- internal ----------

    def _mark_dirty(self):
        self._dirty = True
        self.updated_at = int(time.time())
        if self.manager:
            self.manager.on_state_dirty(self)

    # ---------- properties ----------

    @property
    def current_lottery_times(self):
        return self._current_lottery_times

    @current_lottery_times.setter
    def current_lottery_times(self, value):
        self._current_lottery_times = value
        self._mark_dirty()

    @property
    def total_lottery_times(self):
        return self._total_lottery_times

    @total_lottery_times.setter
    def total_lottery_times(self, value):
        self._total_lottery_times = value
        self._mark_dirty()

    @property
    def item_pool_is_lottery(self):
        return self._item_pool_is_lottery

    @item_pool_is_lottery.setter
    def item_pool_is_lottery(self, value: bool):
        self._item_pool_is_lottery = value
        self._mark_dirty()

    @property
    def air_times(self):
        return self._air_times

    @air_times.setter
    def air_times(self, value):
        self._air_times = value
        self._mark_dirty()



class LotteryStateManager(SingletonSQLiteManager):
    DB_NAME = "lottery.db"
    DB_PATH = "database/lottery.db"

    def __init__(self, debug=False):
        if not self._init_sqlite_manager(debug):
            return

        self._states: dict[str, LotteryState] = {}   # user_id -> state
        self._dirty_states: set[str] = set()

        self._init_schema()

    # ---------- schema ----------

    def _init_schema(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS lottery_state (
            user_id TEXT PRIMARY KEY,
            current_lottery_times INTEGER NOT NULL,
            total_lottery_times INTEGER NOT NULL,
            item_pool_is_lottery INTEGER NOT NULL,
            air_times INTEGER NOT NULL,
            updated_at INTEGER NOT NULL
        )
        """)
        self.conn.commit()

    # ---------- state interaction ----------

    def get(self, user_id: str) -> LotteryState:
        user_id = str(user_id)
        if user_id in self._states:
            return self._states[user_id]

        with self._lock:
            self.cursor.execute("""
                SELECT user_id,
                       current_lottery_times,
                       total_lottery_times,
                       item_pool_is_lottery,
                       air_times,
                       updated_at
                FROM lottery_state
                WHERE user_id = ?
            """, (user_id,))
            row = self.cursor.fetchone()

            if row:
                state = LotteryState.from_row(row, manager=self)
            else:
                state = LotteryState.new(user_id, manager=self)
                self.insert(state)

            self._states[user_id] = state
            return state

    def on_state_dirty(self, state: LotteryState):
        with self._lock:
            self._dirty_states.add(state.user_id)
            self.flush()

    # ---------- persistence ----------

    def insert(self, state: LotteryState):
        with self._lock:
            self.cursor.execute("""
            INSERT OR REPLACE INTO lottery_state VALUES (?, ?, ?, ?, ?, ?)
            """, (
                state.user_id,
                state.current_lottery_times,
                state.total_lottery_times,
                int(state.item_pool_is_lottery),
                state.air_times,
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
                UPDATE lottery_state
                SET current_lottery_times = ?,
                    total_lottery_times = ?,
                    item_pool_is_lottery = ?,
                    air_times = ?,
                    updated_at = ?
                WHERE user_id = ?
                """, (
                    state.current_lottery_times,
                    state.total_lottery_times,
                    int(state.item_pool_is_lottery),
                    state.air_times,
                    state.updated_at,
                    state.user_id
                ))

                self._dirty_states.discard(user_id)

            self.conn.commit()

    def load_all_states(self):
        with self._lock:
            self.cursor.execute("""
                SELECT user_id,
                       current_lottery_times,
                       total_lottery_times,
                       item_pool_is_lottery,
                       air_times,
                       updated_at
                FROM lottery_state
            """)
            for row in self.cursor.fetchall():
                state = LotteryState.from_row(row, manager=self)
                self._states[state.user_id] = state

    def reset_daily_item_pool_flags(self):
        with self._lock:
            self.load_all_states()
            for state in self._states.values():
                state._item_pool_is_lottery = False

            self.cursor.execute(
                "UPDATE lottery_state SET item_pool_is_lottery = 0, updated_at = ?",
                (int(time.time()),)
            )
            self.conn.commit()

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
