from __future__ import annotations

import sqlite3
from aiohttp import web


def json_error(code: str, *, status: int) -> web.Response:
    return web.json_response({"error": code}, status=status)


def json_ok(payload: dict, *, status: int = 200) -> web.Response:
    return web.json_response(payload, status=status)


def is_sqlite_busy_or_locked(err: sqlite3.OperationalError) -> bool:
    msg = str(err).lower()
    return ("locked" in msg) or ("busy" in msg)


def sqlite_error_response(logger, *, action: str, err: sqlite3.OperationalError) -> web.Response:
    if is_sqlite_busy_or_locked(err):
        logger.warning("SQLite busy/locked while %s: %s", action, err)
        return json_error("db_locked", status=503)

    logger.exception("SQLite error while %s: %s", action, err)
    return json_error("db_error", status=500)


def normalize_email(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    email = value.strip().lower()
    if not email or "@" not in email:
        return None
    return email


def require_str(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    s = value.strip()
    return s if s else None
