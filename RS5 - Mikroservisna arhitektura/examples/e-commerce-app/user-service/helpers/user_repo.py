import sqlite3
import uuid
from pathlib import Path

from .sqlite_utils import connect


def list_users(db_path: Path) -> list[dict[str, object]]:
    if not db_path.exists():
        return []

    with connect(db_path) as conn:
        rows = conn.execute(
            "SELECT id, email, connection FROM users ORDER BY id ASC;"
        ).fetchall()
        return [{"id": r[0], "email": r[1], "connection": r[2]} for r in rows]


def ensure_user(
    db_path: Path, *, email: str, connection: str
) -> tuple[bool, str | None]:
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with connect(db_path) as conn:
        row = conn.execute("SELECT id FROM users WHERE email=?;", (email,)).fetchone()
        if row:
            return False, str(row[0])

        user_id = str(uuid.uuid4())
        try:
            conn.execute(
                "INSERT INTO users (id, email, connection) VALUES (?, ?, ?);",
                (user_id, email, connection),
            )
            conn.commit()
            return True, user_id
        except sqlite3.IntegrityError:
            row = conn.execute(
                "SELECT id FROM users WHERE email=?;", (email,)
            ).fetchone()
            return False, (str(row[0]) if row else None)
