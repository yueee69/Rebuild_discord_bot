import sqlite3
import threading
from pathlib import Path

from .lifecycle import register


class SingletonSQLiteManager:
    DB_NAME = ""

    def __new__(cls, *args, **kwargs):
        lock = cls.__dict__.get("_instance_lock")
        if lock is None:
            lock = threading.Lock()
            cls._instance_lock = lock

        with lock:
            instance = cls.__dict__.get("_instance")
            if instance is None:
                instance = super().__new__(cls)
                instance._initialized = False
                cls._instance = instance
            return instance

    def _init_sqlite_manager(self, debug: bool = False) -> bool:
        if getattr(self, "_initialized", False) and not getattr(self, "_closed", False):
            return False

        self.debug = debug
        self._lock = threading.RLock()
        self._closed = False

        db_path = Path(__file__).resolve().parent.parent / "database" / self.DB_NAME
        db_path.parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA journal_mode=WAL")
        self.cursor.execute("PRAGMA foreign_keys=ON")

        self._initialized = True
        register(self)
        return True

    def _table_is_empty(self, table_name: str) -> bool:
        self.cursor.execute(f"SELECT 1 FROM {table_name} LIMIT 1")
        return self.cursor.fetchone() is None

    def close(self):
        with self._lock:
            if getattr(self, "_closed", False):
                return
            try:
                flush = getattr(self, "flush", None)
                if callable(flush):
                    flush()
                self.conn.close()
            finally:
                self._closed = True
                self.conn = None
                self.cursor = None
