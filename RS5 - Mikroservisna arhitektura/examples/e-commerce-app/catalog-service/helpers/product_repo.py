import sqlite3
import uuid
from pathlib import Path

from .sqlite_utils import connect


PRODUCT_COLUMNS = [
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


def list_products(db_path: Path) -> list[dict[str, object]]:
    if not db_path.exists():
        return []

    with connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT id, name, category, price, currency, description, shipping_time, amount_available, public_image_url
            FROM products
            ORDER BY name ASC;
            """.strip()
        ).fetchall()

        return [
            {
                "id": r[0],
                "name": r[1],
                "category": r[2],
                "price": r[3],
                "currency": r[4],
                "description": r[5],
                "shipping_time": r[6],
                "amount_available": r[7],
                "public_image_url": r[8],
            }
            for r in rows
        ]


def get_product(db_path: Path, *, product_id: str) -> dict[str, object] | None:
    if not db_path.exists():
        return None

    with connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT id, name, category, price, currency, description, shipping_time, amount_available, public_image_url
            FROM products
            WHERE id = ?
            LIMIT 1;
            """.strip(),
            (product_id,),
        ).fetchone()

        if not row:
            return None

        return {
            "id": row[0],
            "name": row[1],
            "category": row[2],
            "price": row[3],
            "currency": row[4],
            "description": row[5],
            "shipping_time": row[6],
            "amount_available": row[7],
            "public_image_url": row[8],
        }


def create_product(
    db_path: Path,
    *,
    name: str,
    category: str,
    price: float,
    currency: str,
    description: str,
    shipping_time: str,
    amount_available: int,
    public_image_url: str,
) -> str:
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with connect(db_path) as conn:
        product_id = str(uuid.uuid4())
        conn.execute(
            """
            INSERT INTO products (
              id, name, category, price, currency, description, shipping_time, amount_available, public_image_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """.strip(),
            (
                product_id,
                name,
                category,
                price,
                currency,
                description,
                shipping_time,
                amount_available,
                public_image_url,
            ),
        )
        conn.commit()
        return product_id


def update_product(
    db_path: Path,
    *,
    product_id: str,
    name: str,
    category: str,
    price: float,
    currency: str,
    description: str,
    shipping_time: str,
    amount_available: int,
    public_image_url: str,
) -> bool:
    if not db_path.exists():
        return False

    with connect(db_path) as conn:
        cur = conn.execute(
            """
            UPDATE products
            SET name=?, category=?, price=?, currency=?, description=?, shipping_time=?, amount_available=?, public_image_url=?
            WHERE id=?;
            """.strip(),
            (
                name,
                category,
                price,
                currency,
                description,
                shipping_time,
                amount_available,
                public_image_url,
                product_id,
            ),
        )
        conn.commit()
        return cur.rowcount > 0


def delete_product(db_path: Path, *, product_id: str) -> bool:
    if not db_path.exists():
        return False

    with connect(db_path) as conn:
        cur = conn.execute("DELETE FROM products WHERE id=?;", (product_id,))
        conn.commit()
        return cur.rowcount > 0


def clear_products(db_path: Path) -> int:
    """
    Delete all products from the database.

    Returns the number of deleted rows.
    """
    if not db_path.exists():
        return 0

    with connect(db_path) as conn:
        cur = conn.execute("DELETE FROM products;")
        conn.commit()
        return int(cur.rowcount)


def product_exists(db_path: Path, *, product_id: str) -> bool:
    if not db_path.exists():
        return False

    with connect(db_path) as conn:
        row = conn.execute(
            "SELECT 1 FROM products WHERE id=? LIMIT 1;", (product_id,)
        ).fetchone()
        return row is not None


def check_availability(
    db_path: Path, *, items: list[tuple[str, int]]
) -> dict[str, object]:
    """
    Check whether all requested items are available in requested quantities.
    """
    if not db_path.exists():
        return {"ok": False, "reason": "db_missing", "items": []}

    details: list[dict[str, object]] = []
    ok = True

    with connect(db_path) as conn:
        for product_id, qty in items:
            row = conn.execute(
                "SELECT amount_available FROM products WHERE id=? LIMIT 1;",
                (product_id,),
            ).fetchone()
            if not row:
                ok = False
                details.append(
                    {
                        "item_id": product_id,
                        "requested": qty,
                        "available": 0,
                        "ok": False,
                        "reason": "not_found",
                    }
                )
                continue

            available = int(row[0] or 0)
            item_ok = available >= int(qty)
            if not item_ok:
                ok = False
            details.append(
                {
                    "item_id": product_id,
                    "requested": int(qty),
                    "available": available,
                    "ok": bool(item_ok),
                    "reason": None if item_ok else "insufficient_stock",
                }
            )

    return {"ok": bool(ok), "items": details}


def decrement_stock(
    db_path: Path, *, items: list[tuple[str, int]]
) -> dict[str, object]:
    """
    Decrease stock for all items. Operation is all-or-nothing.
    """
    if not db_path.exists():
        return {"ok": False, "reason": "db_missing"}

    with connect(db_path) as conn:
        try:
            conn.execute("BEGIN IMMEDIATE;")
            # Verify and decrement per item atomically.
            for product_id, qty in items:
                cur = conn.execute(
                    """
                    UPDATE products
                    SET amount_available = amount_available - ?
                    WHERE id = ? AND amount_available >= ?;
                    """.strip(),
                    (int(qty), product_id, int(qty)),
                )
                if cur.rowcount != 1:
                    # Not found or insufficient stock; rollback.
                    conn.rollback()
                    check = check_availability(db_path, items=items)
                    return {"ok": False, "reason": "insufficient_stock", "check": check}

            conn.commit()
            return {"ok": True}
        except sqlite3.OperationalError as e:
            try:
                conn.rollback()
            except Exception:
                pass
            return {"ok": False, "reason": "db_error", "message": str(e)}
