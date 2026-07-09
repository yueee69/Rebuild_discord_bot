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

        self._db_path = Path(__file__).resolve().parent.parent / "database" / self.DB_NAME
        self._db_path.parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(self._db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA journal_mode=WAL")
        self.cursor.execute("PRAGMA foreign_keys=ON")
        self._remember_database_signature()

        self._initialized = True
        register(self)
        return True

    def _database_signature(self):
        paths = [
            self._db_path,
            Path(f"{self._db_path}-wal"),
            Path(f"{self._db_path}-shm"),
        ]
        signature = []
        for path in paths:
            if path.exists():
                stat = path.stat()
                signature.append((str(path), stat.st_mtime_ns, stat.st_size))
            else:
                signature.append((str(path), None, None))
        return tuple(signature)

    def _remember_database_signature(self):
        self._db_signature = self._database_signature()

    def _database_changed(self) -> bool:
        return getattr(self, "_db_signature", None) != self._database_signature()

    def _reload_if_database_changed(self):
        if getattr(self, "_closed", False):
            return
        if not self._database_changed():
            return

        reload = getattr(self, "reload_from_database", None)
        if callable(reload):
            reload()

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
