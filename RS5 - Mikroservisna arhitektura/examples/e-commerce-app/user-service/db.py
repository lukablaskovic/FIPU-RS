from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

from logging_setup import logging_setup


DEFAULT_DB_PATH = Path(__file__).with_name("users.db") # Putanja do zadane SQLite baze

EXPECTED_USER_COLUMNS = [
    "id",
    "email",
    "connection",
]

DDL_USERS = """
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  connection TEXT NOT NULL
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
    """
    Minimal schema check (beyond just column names) so we can detect migrations
    like INTEGER id -> TEXT uuid.
    """
    info = _get_table_info(conn, "users")
    by_name = {c["name"]: c for c in info}

    id_col = by_name.get("id")
    email_col = by_name.get("email")
    connection_col = by_name.get("connection")

    if not id_col or not email_col or not connection_col:
        return False

    if id_col["type"] != "TEXT" or id_col["pk"] != 1:
        return False
    if email_col["type"] != "TEXT" or email_col["notnull"] != 1:
        return False
    if connection_col["type"] != "TEXT" or connection_col["notnull"] != 1:
        return False

    return True


def _ensure_users_table(conn: sqlite3.Connection, *, reset: bool) -> None:
    if _table_exists(conn, "users"):
        actual = _get_table_columns(conn, "users")
        if actual != EXPECTED_USER_COLUMNS or not _schema_matches(conn):
            if not reset:
                logger.error(
                    "Existing `users` table schema mismatch. expected=%s actual=%s",
                    EXPECTED_USER_COLUMNS,
                    actual,
                )
                raise RuntimeError(
                    "Existing `users` table schema does not match expected schema.\n"
                    f"Expected columns: {EXPECTED_USER_COLUMNS}\n"
                    f"Actual columns:   {actual}\n"
                    "Re-run with --reset to drop and recreate the table."
                )
            logger.warning("Dropping existing `users` table (reset enabled).")
            conn.execute("DROP TABLE users;")

    conn.execute(DDL_USERS)


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
                    logger.warning("Could not enable WAL mode, current mode: %s", result[0] if result else "unknown")
        except sqlite3.OperationalError as e:
            logger.warning("Could not set WAL mode (database may be locked): %s", e)
        _ensure_users_table(conn, reset=reset)
        conn.commit()


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize user-service SQLite database")
    parser.add_argument(
        "--db",
        dest="db_path",
        default=str(DEFAULT_DB_PATH),
        help=f"Path to sqlite db file (default: {DEFAULT_DB_PATH})",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Drop and recreate the `users` table if it exists with a different schema",
    )
    args = parser.parse_args()

    db_path = Path(args.db_path).expanduser().resolve()
    init_db(db_path, reset=bool(args.reset)) # inicijalizacija baze podataka i resetiranje tablice ako je potrebno
    
    logger.info("SQLite DB initialized: %s", db_path)
    logger.info("Ensured table schema: users(%s)", ", ".join(EXPECTED_USER_COLUMNS))
    return 0

# python3 db.py --db users.db

if __name__ == "__main__":
    raise SystemExit(main())
