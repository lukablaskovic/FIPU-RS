from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

from logging_setup import logging_setup


DEFAULT_DB_PATH = Path(__file__).with_name("products.db")

EXPECTED_PRODUCT_COLUMNS = [
    "id",
    "name",
    "category",
    "price",
    "currency",
    "description",
    "shipping_time",
    "amount_available",
    "public_image_url",
]

DDL_PRODUCTS = """
CREATE TABLE IF NOT EXISTS products (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  category TEXT NOT NULL,
  price REAL NOT NULL,
  currency TEXT NOT NULL,
  description TEXT NOT NULL,
  shipping_time TEXT NOT NULL,
  amount_available INTEGER NOT NULL,
  public_image_url TEXT NOT NULL
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


def _get_table_info(conn: sqlite3.Connection, table: str) -> list[dict[str, object]]:
    rows = conn.execute(f"PRAGMA table_info({table});").fetchall()
    return [
        {
            "name": r[1],
            "type": (r[2] or "").upper(),
            "notnull": int(r[3]),
            "pk": int(r[5]),
        }
        for r in rows
    ]


def _schema_matches(conn: sqlite3.Connection) -> bool:
    info = _get_table_info(conn, "products")
    by_name = {c["name"]: c for c in info}

    id_col = by_name.get("id")
    name_col = by_name.get("name")
    category_col = by_name.get("category")
    price_col = by_name.get("price")
    currency_col = by_name.get("currency")
    description_col = by_name.get("description")
    shipping_time_col = by_name.get("shipping_time")
    amount_available_col = by_name.get("amount_available")
    public_image_url_col = by_name.get("public_image_url")

    if (
        not id_col
        or not name_col
        or not category_col
        or not price_col
        or not currency_col
        or not description_col
        or not shipping_time_col
        or not amount_available_col
        or not public_image_url_col
    ):
        return False

    if id_col["type"] != "TEXT" or id_col["pk"] != 1:
        return False

    for col_name in [
        "name",
        "category",
        "price",
        "currency",
        "description",
        "shipping_time",
        "amount_available",
        "public_image_url",
    ]:
        col = by_name.get(col_name)
        if not col or col["notnull"] != 1:
            return False

    return True


def _ensure_products_table(conn: sqlite3.Connection, *, reset: bool) -> None:
    if _table_exists(conn, "products"):
        actual = _get_table_columns(conn, "products")
        if actual != EXPECTED_PRODUCT_COLUMNS or not _schema_matches(conn):
            if not reset:
                logger.error(
                    "Existing `products` table schema mismatch. expected=%s actual=%s",
                    EXPECTED_PRODUCT_COLUMNS,
                    actual,
                )
                raise RuntimeError(
                    "Existing `products` table schema does not match expected schema.\n"
                    f"Expected columns: {EXPECTED_PRODUCT_COLUMNS}\n"
                    f"Actual columns:   {actual}\n"
                    "Re-run with --reset to drop and recreate the table."
                )
            logger.warning("Dropping existing `products` table (reset enabled).")
            conn.execute("DROP TABLE products;")

    conn.execute(DDL_PRODUCTS)


def init_db(db_path: Path, *, reset: bool) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path, timeout=20.0) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        # Try to enable WAL mode, but don't fail if database is locked
        try:
            current_mode = conn.execute("PRAGMA journal_mode;").fetchone()
            if current_mode and current_mode[0].lower() != "wal":
                result = conn.execute("PRAGMA journal_mode = WAL;").fetchone()
                if result and result[0].lower() == "wal":
                    logger.info("WAL mode enabled successfully")
                else:
                    logger.warning(
                        "Could not enable WAL mode, current mode: %s",
                        result[0] if result else "unknown",
                    )
        except sqlite3.OperationalError as e:
            logger.warning("Could not set WAL mode (database may be locked): %s", e)

        _ensure_products_table(conn, reset=reset)
        conn.commit()


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize catalog-service SQLite database")
    parser.add_argument(
        "--db",
        dest="db_path",
        default=str(DEFAULT_DB_PATH),
        help=f"Path to sqlite db file (default: {DEFAULT_DB_PATH})",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Drop and recreate the `products` table if it exists with a different schema",
    )
    args = parser.parse_args()

    db_path = Path(args.db_path).expanduser().resolve()
    init_db(db_path, reset=bool(args.reset))

    logger.info("SQLite DB initialized: %s", db_path)
    logger.info("Ensured table schema: products(%s)", ", ".join(EXPECTED_PRODUCT_COLUMNS))
    return 0


# python3 db.py --db products.db

if __name__ == "__main__":
    raise SystemExit(main())
