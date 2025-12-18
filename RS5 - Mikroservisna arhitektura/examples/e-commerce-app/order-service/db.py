from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

from logging_setup import logging_setup


DEFAULT_DB_PATH = Path(__file__).with_name("orders.db")

EXPECTED_ORDER_COLUMNS = [
    "id",
    "user_id",
    "name",
    "surname",
    "delivery_address",
    "phone_number",
    "email_address",
    "client_request_id",
    "created_at",
]

EXPECTED_ORDER_ITEM_COLUMNS = [
    "id",
    "order_id",
    "item_id",
    "ordered_quantity",
]

DDL_ORDERS = """
CREATE TABLE IF NOT EXISTS orders (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  name TEXT NOT NULL,
  surname TEXT NOT NULL,
  delivery_address TEXT NOT NULL,
  phone_number TEXT NOT NULL,
  email_address TEXT NOT NULL,
  client_request_id TEXT UNIQUE,
  created_at TEXT NOT NULL
);
""".strip()

DDL_ORDER_ITEMS = """
CREATE TABLE IF NOT EXISTS order_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id TEXT NOT NULL,
  item_id TEXT NOT NULL,
  ordered_quantity INTEGER NOT NULL,
  FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE
);
""".strip()

logger = logging_setup.get_logger()


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1;", (table,)
    ).fetchone()
    return row is not None


def _get_table_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    rows = conn.execute(f"PRAGMA table_info({table});").fetchall()
    return [r[1] for r in rows]


def _ensure_table(
    conn: sqlite3.Connection,
    *,
    table: str,
    ddl: str,
    expected_columns: list[str],
    reset: bool,
) -> None:
    if _table_exists(conn, table):
        actual = _get_table_columns(conn, table)
        if actual != expected_columns:
            if not reset:
                logger.error(
                    "Existing `%s` table schema mismatch. expected=%s actual=%s",
                    table,
                    expected_columns,
                    actual,
                )
                raise RuntimeError(
                    f"Existing `{table}` table schema does not match expected schema. "
                    "Re-run with --reset to drop and recreate the tables."
                )
            logger.warning("Dropping existing `%s` table (reset enabled).", table)
            conn.execute(f"DROP TABLE {table};")

    conn.execute(ddl)


def _ensure_tables(conn: sqlite3.Connection, *, reset: bool) -> None:
    if reset:
        if _table_exists(conn, "order_items"):
            conn.execute("DROP TABLE order_items;")
        if _table_exists(conn, "orders"):
            conn.execute("DROP TABLE orders;")

    _ensure_table(
        conn,
        table="orders",
        ddl=DDL_ORDERS,
        expected_columns=EXPECTED_ORDER_COLUMNS,
        reset=False,
    )
    _ensure_table(
        conn,
        table="order_items",
        ddl=DDL_ORDER_ITEMS,
        expected_columns=EXPECTED_ORDER_ITEM_COLUMNS,
        reset=False,
    )


def init_db(db_path: Path, *, reset: bool) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path, timeout=20.0) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            conn.execute("PRAGMA journal_mode = WAL;")
        except sqlite3.OperationalError as e:
            logger.warning("Could not set WAL mode (database may be locked): %s", e)

        _ensure_tables(conn, reset=reset)
        conn.commit()


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize order-service SQLite database")
    parser.add_argument(
        "--db",
        dest="db_path",
        default=str(DEFAULT_DB_PATH),
        help=f"Path to sqlite db file (default: {DEFAULT_DB_PATH})",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Drop and recreate the `orders` table if it exists with a different schema",
    )
    args = parser.parse_args()

    db_path = Path(args.db_path).expanduser().resolve()
    init_db(db_path, reset=bool(args.reset))

    logger.info("SQLite DB initialized: %s", db_path)
    logger.info("Ensured table schema: orders(%s)", ", ".join(EXPECTED_ORDER_COLUMNS))
    logger.info("Ensured table schema: order_items(%s)", ", ".join(EXPECTED_ORDER_ITEM_COLUMNS))
    return 0


# python3 db.py --db orders.db

if __name__ == "__main__":
    raise SystemExit(main())
