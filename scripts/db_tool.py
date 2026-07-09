from __future__ import annotations

import argparse
import csv
import random
import shutil
import sqlite3
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
DATABASE_DIR = ROOT_DIR / "database"
BACKUP_DIR = DATABASE_DIR / "backups"
DEFAULT_LIMIT = 50


def example_main():
    """
    Put your one-off maintenance calls here, then run:

        python .\scripts\db_tool.py run-main

    Examples:
        set_user_coin(579618807237312512, 10000)
        add_user_fortune(579618807237312512, 5)
        set_item_cards(579618807237312512, nick=3, role=2)
        refresh_daily_shop()
        show_user(579618807237312512)
    """
    show_databases()


def main() -> int:
    add_user_coin(579618807237312512, 100000)

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Small SQLite maintenance tool for bot databases.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_dbs = subparsers.add_parser("list-dbs", help="List database files.")
    list_dbs.set_defaults(func=list_databases)

    tables = subparsers.add_parser("tables", help="List tables in a database.")
    tables.add_argument("db", help="Database name, for example user.db.")
    tables.set_defaults(func=list_tables)

    schema = subparsers.add_parser("schema", help="Show table schema.")
    schema.add_argument("db", help="Database name.")
    schema.add_argument("table", nargs="?", help="Table name. Omit to show all tables.")
    schema.set_defaults(func=show_schema)

    select = subparsers.add_parser("select", help="Select rows from a table.")
    select.add_argument("db", help="Database name.")
    select.add_argument("table", help="Table name.")
    select.add_argument("--columns", default="*", help="Columns to select. Default: *")
    select.add_argument("--where", default="", help="SQL WHERE clause without the WHERE keyword.")
    select.add_argument("--order-by", default="", help="SQL ORDER BY clause without the ORDER BY keyword.")
    select.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help=f"Row limit. Default: {DEFAULT_LIMIT}")
    select.add_argument("--csv", action="store_true", help="Print result as CSV.")
    select.set_defaults(func=select_rows)

    execute = subparsers.add_parser("exec", help="Execute SQL. Backs up the database by default.")
    execute.add_argument("db", help="Database name.")
    execute.add_argument("sql", help="SQL to execute. Use quotes around it.")
    execute.add_argument("--no-backup", action="store_true", help="Do not create a backup before executing.")
    execute.add_argument("--yes", action="store_true", help="Skip confirmation prompt.")
    execute.set_defaults(func=execute_sql)

    backup = subparsers.add_parser("backup", help="Create a database backup.")
    backup.add_argument("db", help="Database name.")
    backup.set_defaults(func=backup_database_command)

    run_main = subparsers.add_parser("run-main", help="Run example_main() in this file.")
    run_main.set_defaults(func=lambda args: run_example_main())

    return parser


# ======== direct-use helpers ========


def run_example_main() -> int:
    example_main()
    return 0


def show_databases():
    rows = [(path.name, path.stat().st_size) for path in sorted(DATABASE_DIR.glob("*.db"))]
    print_table(["database", "bytes"], rows)


def show_user(user_id: int | str):
    row = get_user(user_id)
    if not row:
        print(f"user {user_id} not found")
        return
    print_table(row.keys(), [tuple(row)])


def get_user(user_id: int | str) -> sqlite3.Row | None:
    with connect("user.db") as conn:
        return conn.execute(
            "SELECT * FROM account_state WHERE user_id = ?",
            (str(user_id),),
        ).fetchone()


def set_user_coin(user_id: int | str, coin: int, *, backup: bool = True):
    update_user_fields(user_id, backup=backup, coin=int(coin))


def add_user_coin(user_id: int | str, amount: int, *, backup: bool = True):
    user = require_user(user_id)
    set_user_coin(user_id, int(user["coin"]) + int(amount), backup=backup)


def set_user_fortune(user_id: int | str, fortune: int, *, backup: bool = True):
    update_user_fields(user_id, backup=backup, fortune=int(fortune))


def add_user_fortune(user_id: int | str, amount: int, *, backup: bool = True):
    user = require_user(user_id)
    set_user_fortune(user_id, int(user["fortune"]) + int(amount), backup=backup)


def set_user_level(user_id: int | str, level: int, *, backup: bool = True):
    update_user_fields(user_id, backup=backup, level=int(level))


def reset_user_daily_activity(user_id: int | str, *, backup: bool = True):
    update_user_fields(
        user_id,
        backup=backup,
        chat_today=0,
        voice_today=0,
        stream_today=0,
    )


def update_user_fields(user_id: int | str, *, backup: bool = True, **fields):
    allowed = {
        "coin",
        "fortune",
        "total_gain",
        "level",
        "chat_today",
        "voice_today",
        "stream_today",
    }
    unknown = set(fields) - allowed
    if unknown:
        raise ValueError(f"Unknown user fields: {sorted(unknown)}")
    if not fields:
        return

    maybe_backup("user.db", backup)
    fields["updated_at"] = int(time.time())
    assignments = ", ".join(f"{field} = ?" for field in fields)
    params = [int(value) for value in fields.values()]
    params.append(str(user_id))

    with connect("user.db") as conn:
        cursor = conn.execute(
            f"UPDATE account_state SET {assignments} WHERE user_id = ?",
            params,
        )
        conn.commit()
        if cursor.rowcount == 0:
            raise ValueError(f"user {user_id} not found. Use /用戶資訊 first.")


def require_user(user_id: int | str) -> sqlite3.Row:
    user = get_user(user_id)
    if not user:
        raise ValueError(f"user {user_id} not found. Use /用戶資訊 first.")
    return user


def show_item_cards(user_id: int | str):
    row = get_item_cards(user_id)
    if not row:
        print(f"item data for {user_id} not found")
        return
    print_table(row.keys(), [tuple(row)])


def get_item_cards(user_id: int | str) -> sqlite3.Row | None:
    with connect("item.db") as conn:
        return conn.execute(
            "SELECT * FROM item_state WHERE user_id = ?",
            (str(user_id),),
        ).fetchone()


def set_item_cards(
    user_id: int | str,
    *,
    trans: int | None = None,
    nick: int | None = None,
    role: int | None = None,
    add_role: int | None = None,
    protect: bool | None = None,
    lottery: bool | None = None,
    backup: bool = True,
):
    fields = {
        "trans": trans,
        "nick": nick,
        "role": role,
        "add_role": add_role,
        "protect": None if protect is None else int(bool(protect)),
        "lottery": None if lottery is None else int(bool(lottery)),
    }
    fields = {key: value for key, value in fields.items() if value is not None}
    if not fields:
        return

    maybe_backup("item.db", backup)
    ensure_item_user(user_id)
    fields["updated_at"] = int(time.time())
    assignments = ", ".join(f"{field} = ?" for field in fields)
    params = [int(value) for value in fields.values()]
    params.append(str(user_id))

    with connect("item.db") as conn:
        conn.execute(f"UPDATE item_state SET {assignments} WHERE user_id = ?", params)
        conn.commit()


def add_item_cards(
    user_id: int | str,
    *,
    trans: int = 0,
    nick: int = 0,
    role: int = 0,
    add_role: int = 0,
    backup: bool = True,
):
    current = get_item_cards(user_id)
    if not current:
        ensure_item_user(user_id)
        current = get_item_cards(user_id)

    set_item_cards(
        user_id,
        trans=int(current["trans"]) + int(trans),
        nick=int(current["nick"]) + int(nick),
        role=int(current["role"]) + int(role),
        add_role=int(current["add_role"]) + int(add_role),
        backup=backup,
    )


def ensure_item_user(user_id: int | str):
    now = int(time.time())
    with connect("item.db") as conn:
        conn.execute("""
            INSERT OR IGNORE INTO item_state
            (user_id, trans, nick, role, add_role, protect, lottery, updated_at)
            VALUES (?, 0, 0, 0, 0, 0, 0, ?)
        """, (str(user_id), now))
        conn.commit()


def show_daily_shop():
    rows = table_rows("daily_shop.db", "daily_shop_goods", order_by="position", limit=-1)
    print_rows(rows)


def refresh_daily_shop(*, backup: bool = True):
    maybe_backup("daily_shop.db", backup)
    items = weighted_unique_daily_shop_items()
    now = int(time.time())
    with connect("daily_shop.db") as conn:
        conn.execute("DELETE FROM daily_shop_goods")
        for position, item in enumerate(items):
            conn.execute("""
                INSERT INTO daily_shop_goods
                (position, item, price, left_count, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                position,
                item["name"],
                item["price"],
                item["left_count"],
                now,
            ))
        conn.commit()
    show_daily_shop()


def dump_fake_lottery_history(user_id: int | str, count: int = 8, *, backup: bool = True):
    maybe_backup("history.db", backup)
    prizes = [
        "空氣",
        "鮭魚幣+500",
        "鮭魚幣+1000",
        "3陽壽",
        "指定暱稱卡",
        "指定身分組卡",
        "增加身分組卡",
        "迴轉卡",
    ]
    pools = ["norm_pool", "item_pool"]
    now = int(time.time())
    with connect("history.db") as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS lottery_history_entries (
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
        next_user_entry_id = conn.execute("""
            SELECT COALESCE(MAX(user_entry_id), 0) + 1
            FROM lottery_history_entries
            WHERE user_id = ?
        """, (str(user_id),)).fetchone()[0]
        for index in range(int(count)):
            created_at = now - index * 60
            pool = pools[index % len(pools)]
            rarity = "大獎" if index == 0 and pool == "norm_pool" else "一般" if pool == "norm_pool" else ""
            pity_before = index if pool == "norm_pool" else None
            pity_after = 0 if rarity == "大獎" else index + 1 if pool == "norm_pool" else None
            is_pity_reset = int(rarity == "大獎")
            conn.execute("""
                INSERT INTO lottery_history_entries
                (user_id, user_entry_id, prize, pool, rarity, pity_before, pity_after, is_pity_reset, display_time, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(user_id),
                next_user_entry_id + index,
                prizes[index % len(prizes)],
                pool,
                rarity,
                pity_before,
                pity_after,
                is_pity_reset,
                format_history_time(created_at),
                created_at,
            ))
        conn.commit()


def format_history_time(timestamp: int) -> str:
    from core import constants

    dt = datetime.fromtimestamp(timestamp, timezone(timedelta(hours=constants.TIME_ZONE)))
    return f"{dt.year} / {dt.month:02d} / {dt.day:02d} | {dt.hour:02d} : {dt.minute:02d} : {dt.second:02d}"


def weighted_unique_daily_shop_items() -> list[dict]:
    from core import constants

    pool = [
        {
            "name": name,
            "base_price": price,
            "discount_percent": discount_percent,
            "weight": weight,
        }
        for name, price, discount_percent, weight in constants.DAILY_SHOP_DEFAULT_ITEMS
        if not any(keyword in name for keyword in constants.DAILY_SHOP_DISABLED_VISIBLE_ITEM_KEYWORDS)
    ]

    count = min(constants.DAILY_SHOP_RANDOM_GOODS_COUNT, len(pool))
    selected_items = []
    for _ in range(count):
        selected = random.choices(pool, weights=[item["weight"] for item in pool], k=1)[0]
        pool.remove(selected)
        selected_items.append({
            "name": selected["name"],
            "price": int(selected["base_price"] * selected["discount_percent"] / 100),
            "left_count": random.randint(
                constants.DAILY_SHOP_LEFT_COUNT_MIN,
                constants.DAILY_SHOP_LEFT_COUNT_MAX,
            ),
        })
    return selected_items


def table_rows(
    db_name: str,
    table: str,
    *,
    columns: str = "*",
    where: str = "",
    order_by: str = "",
    limit: int = DEFAULT_LIMIT,
) -> list[sqlite3.Row]:
    ensure_identifier(table)
    for column in parse_columns(columns):
        ensure_identifier(column)

    safe_columns = ", ".join(quote_identifier(column) for column in parse_columns(columns))
    sql = f"SELECT {safe_columns} FROM {quote_identifier(table)}"
    if where:
        sql += f" WHERE {where}"
    if order_by:
        sql += f" ORDER BY {order_by}"
    params = ()
    if limit >= 0:
        sql += " LIMIT ?"
        params = (limit,)

    with connect(db_name) as conn:
        return conn.execute(sql, params).fetchall()


def maybe_backup(db_name: str, enabled: bool):
    if enabled:
        path = backup_database(resolve_db(db_name))
        print(f"Backup created: {path.relative_to(ROOT_DIR)}")


def list_databases(args) -> int:
    show_databases()
    return 0


def list_tables(args) -> int:
    with connect(args.db) as conn:
        rows = conn.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name
        """).fetchall()

    if not rows:
        print("No tables found.")
        return 0

    for row in rows:
        print(row["name"])
    return 0


def show_schema(args) -> int:
    with connect(args.db) as conn:
        tables = [args.table] if args.table else [
            row["name"]
            for row in conn.execute("""
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                ORDER BY name
            """).fetchall()
        ]

        for table in tables:
            ensure_identifier(table)
            print(f"[{table}]")
            rows = conn.execute(f"PRAGMA table_info({quote_identifier(table)})").fetchall()
            if not rows:
                print("  table not found")
                continue
            for row in rows:
                required = "NOT NULL" if row["notnull"] else "NULL"
                default = f" DEFAULT {row['dflt_value']}" if row["dflt_value"] is not None else ""
                pk = " PRIMARY KEY" if row["pk"] else ""
                print(f"  {row['name']} {row['type']} {required}{default}{pk}")
    return 0


def select_rows(args) -> int:
    ensure_identifier(args.table)
    for column in parse_columns(args.columns):
        ensure_identifier(column)

    columns = ", ".join(quote_identifier(column) for column in parse_columns(args.columns))
    sql = f"SELECT {columns} FROM {quote_identifier(args.table)}"

    if args.where:
        sql += f" WHERE {args.where}"
    if args.order_by:
        sql += f" ORDER BY {args.order_by}"
    if args.limit >= 0:
        sql += " LIMIT ?"
        params = (args.limit,)
    else:
        params = ()

    with connect(args.db) as conn:
        rows = conn.execute(sql, params).fetchall()

    print_rows(rows, as_csv=args.csv)
    return 0


def execute_sql(args) -> int:
    db_path = resolve_db(args.db)
    if not args.no_backup:
        backup_path = backup_database(db_path)
        print(f"Backup created: {backup_path.relative_to(ROOT_DIR)}")

    sql = args.sql.strip()
    if not sql:
        print("SQL is empty.", file=sys.stderr)
        return 1

    if not args.yes and not confirm(sql, db_path.name):
        print("Canceled.")
        return 0

    with connect(args.db) as conn:
        before_changes = conn.total_changes
        conn.executescript(sql)
        conn.commit()
        changed = conn.total_changes - before_changes

    print(f"Done. Changed rows: {changed}")
    return 0


def backup_database_command(args) -> int:
    backup_path = backup_database(resolve_db(args.db))
    print(backup_path.relative_to(ROOT_DIR))
    return 0


def connect(db_name: str) -> sqlite3.Connection:
    conn = sqlite3.connect(resolve_db(db_name))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def resolve_db(db_name: str) -> Path:
    path = Path(db_name)
    if path.is_absolute():
        db_path = path
    else:
        db_path = DATABASE_DIR / path.name

    if db_path.suffix != ".db":
        db_path = db_path.with_suffix(".db")
    if not db_path.exists():
        raise FileNotFoundError(db_path)
    if db_path.parent.resolve() != DATABASE_DIR.resolve():
        raise ValueError("Database must be inside the database directory.")
    return db_path


def backup_database(db_path: Path) -> Path:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"{db_path.stem}_{timestamp}.db"
    shutil.copy2(db_path, backup_path)
    return backup_path


def parse_columns(columns: str) -> list[str]:
    columns = columns.strip()
    if columns == "*":
        return ["*"]
    return [column.strip() for column in columns.split(",") if column.strip()]


def ensure_identifier(identifier: str):
    if identifier == "*":
        return
    parts = [part.strip() for part in identifier.split(".")]
    for part in parts:
        if not part.replace("_", "").isalnum() or not part:
            raise ValueError(f"Unsafe identifier: {identifier}")


def quote_identifier(identifier: str) -> str:
    if identifier == "*":
        return "*"
    return ".".join(f'"{part}"' for part in identifier.split("."))


def print_rows(rows: list[sqlite3.Row], as_csv: bool = False):
    if not rows:
        print("No rows.")
        return

    headers = rows[0].keys()
    if as_csv:
        writer = csv.writer(sys.stdout)
        writer.writerow(headers)
        for row in rows:
            writer.writerow([row[header] for header in headers])
        return

    widths = {
        header: max(len(str(header)), *(len(str(row[header])) for row in rows))
        for header in headers
    }
    print(" | ".join(str(header).ljust(widths[header]) for header in headers))
    print("-+-".join("-" * widths[header] for header in headers))
    for row in rows:
        print(" | ".join(str(row[header]).ljust(widths[header]) for header in headers))


def print_table(headers, rows):
    rows = list(rows)
    if not rows:
        print("No rows.")
        return

    headers = [str(header) for header in headers]
    normalized_rows = [tuple(str(value) for value in row) for row in rows]
    widths = {
        header: max(len(header), *(len(row[index]) for row in normalized_rows))
        for index, header in enumerate(headers)
    }
    print(" | ".join(header.ljust(widths[header]) for header in headers))
    print("-+-".join("-" * widths[header] for header in headers))
    for row in normalized_rows:
        print(" | ".join(row[index].ljust(widths[header]) for index, header in enumerate(headers)))


def confirm(sql: str, db_name: str) -> bool:
    print(f"Database: {db_name}")
    print("SQL:")
    print(sql)
    answer = input("Execute this SQL? Type YES to continue: ")
    return answer == "YES"


if __name__ == "__main__":
    raise SystemExit(main())
