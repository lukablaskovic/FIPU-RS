import secrets
from datetime import datetime, timezone
from pathlib import Path

from .sqlite_utils import connect


ORDER_COLUMNS = [
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

ORDER_ITEM_COLUMNS = [
    "id",
    "order_id",
    "item_id",
    "ordered_quantity",
]


def _rows_to_orders(rows: list[tuple]) -> list[dict[str, object]]:
    """
    Convert joined (orders LEFT JOIN order_items) rows to a list of orders with `items`.
    """
    by_id: dict[str, dict[str, object]] = {}

    for r in rows:
        order_id = str(r[0])
        if order_id not in by_id:
            by_id[order_id] = {
                "id": r[0],
                "user_id": r[1],
                "name": r[2],
                "surname": r[3],
                "delivery_address": r[4],
                "phone_number": r[5],
                "email_address": r[6],
                "client_request_id": r[7],
                "created_at": r[8],
                "items": [],
            }

        item_row_id = r[9]
        if item_row_id is not None:
            items: list[dict[str, object]] = by_id[order_id]["items"]  # type: ignore[assignment]
            items.append(
                {
                    "id": item_row_id,
                    "item_id": r[10],
                    "ordered_quantity": r[11],
                }
            )

    return list(by_id.values())


def list_orders(db_path: Path) -> list[dict[str, object]]:
    if not db_path.exists():
        return []

    with connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT
              o.id, o.user_id, o.name, o.surname, o.delivery_address, o.phone_number, o.email_address, o.client_request_id, o.created_at,
              i.id, i.item_id, i.ordered_quantity
            FROM orders o
            LEFT JOIN order_items i ON i.order_id = o.id
            ORDER BY o.created_at DESC, i.id ASC;
            """.strip()
        ).fetchall()

        return _rows_to_orders(rows)


def get_order(db_path: Path, *, order_id: str) -> dict[str, object] | None:
    if not db_path.exists():
        return None

    with connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT
              o.id, o.user_id, o.name, o.surname, o.delivery_address, o.phone_number, o.email_address, o.client_request_id, o.created_at,
              i.id, i.item_id, i.ordered_quantity
            FROM orders o
            LEFT JOIN order_items i ON i.order_id = o.id
            WHERE o.id = ?
            ORDER BY i.id ASC;
            """.strip(),
            (order_id,),
        ).fetchall()

        if not rows:
            return None

        return _rows_to_orders(rows)[0]


def get_order_by_client_request_id(
    db_path: Path, *, client_request_id: str
) -> dict[str, object] | None:
    if not db_path.exists():
        return None

    with connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT
              o.id, o.user_id, o.name, o.surname, o.delivery_address, o.phone_number, o.email_address, o.client_request_id, o.created_at,
              i.id, i.item_id, i.ordered_quantity
            FROM orders o
            LEFT JOIN order_items i ON i.order_id = o.id
            WHERE o.client_request_id = ?
            ORDER BY i.id ASC;
            """.strip(),
            (client_request_id,),
        ).fetchall()

        if not rows:
            return None
        return _rows_to_orders(rows)[0]


def list_orders_by_user_id(db_path: Path, *, user_id: str) -> list[dict[str, object]]:
    if not db_path.exists():
        return []

    with connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT
              o.id, o.user_id, o.name, o.surname, o.delivery_address, o.phone_number, o.email_address, o.client_request_id, o.created_at,
              i.id, i.item_id, i.ordered_quantity
            FROM orders o
            LEFT JOIN order_items i ON i.order_id = o.id
            WHERE o.user_id = ?
            ORDER BY o.created_at DESC, i.id ASC;
            """.strip(),
            (user_id,),
        ).fetchall()

        return _rows_to_orders(rows)


def clear_orders(db_path: Path) -> dict[str, int]:
    """
    Delete all orders (and their items via FK cascade).
    Returns counts of deleted rows (pre-delete counts).
    """
    if not db_path.exists():
        return {"orders_deleted": 0, "order_items_deleted": 0}

    with connect(db_path) as conn:
        orders_before = int(conn.execute("SELECT COUNT(*) FROM orders;").fetchone()[0])
        items_before = int(
            conn.execute("SELECT COUNT(*) FROM order_items;").fetchone()[0]
        )

        conn.execute("DELETE FROM orders;")
        try:
            conn.execute("DELETE FROM sqlite_sequence WHERE name='order_items';")
        except Exception:
            pass

        conn.commit()

    return {"orders_deleted": orders_before, "order_items_deleted": items_before}


def delete_order(db_path: Path, *, order_id: str) -> bool:
    if not db_path.exists():
        return False

    with connect(db_path) as conn:
        cur = conn.execute("DELETE FROM orders WHERE id=?;", (order_id,))
        conn.commit()
        return cur.rowcount > 0


def create_order(
    db_path: Path,
    *,
    user_id: str,
    items: list[dict[str, object]],
    name: str,
    surname: str,
    delivery_address: str,
    phone_number: str,
    email_address: str,
    client_request_id: str | None = None,
) -> tuple[dict[str, object], bool]:
    db_path.parent.mkdir(parents=True, exist_ok=True)

    if not items:
        raise ValueError("missing_items")

    normalized_items: list[tuple[str, int]] = []
    for it in items:
        item_id = str(it.get("item_id") or "").strip()
        qty_raw = it.get("ordered_quantity")
        try:
            qty = int(qty_raw)  # type: ignore[arg-type]
        except Exception:
            qty = 0

        if not item_id or qty <= 0:
            raise ValueError("invalid_items")
        normalized_items.append((item_id, qty))

    if client_request_id is not None:
        client_request_id = str(client_request_id).strip() or None

    order_id = secrets.token_hex(16)
    created_at = datetime.now(timezone.utc).isoformat()

    with connect(db_path) as conn:
        if client_request_id:
            existing = conn.execute(
                "SELECT id FROM orders WHERE client_request_id = ? LIMIT 1;",
                (client_request_id,),
            ).fetchone()
            if existing and existing[0]:
                found = get_order(db_path, order_id=str(existing[0]))
                if found is not None:
                    return found, False

        conn.execute(
            """
            INSERT INTO orders (
              id, user_id, name, surname, delivery_address, phone_number, email_address, client_request_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """.strip(),
            (
                order_id,
                user_id,
                name,
                surname,
                delivery_address,
                phone_number,
                email_address,
                client_request_id,
                created_at,
            ),
        )

        conn.executemany(
            """
            INSERT INTO order_items (order_id, item_id, ordered_quantity)
            VALUES (?, ?, ?);
            """.strip(),
            [(order_id, iid, int(qty)) for (iid, qty) in normalized_items],
        )
        conn.commit()

    return (
        {
            "id": order_id,
            "user_id": user_id,
            "name": name,
            "surname": surname,
            "delivery_address": delivery_address,
            "phone_number": phone_number,
            "email_address": email_address,
            "client_request_id": client_request_id,
            "created_at": created_at,
            "items": [
                {"item_id": iid, "ordered_quantity": qty}
                for (iid, qty) in normalized_items
            ],
        },
        True,
    )
