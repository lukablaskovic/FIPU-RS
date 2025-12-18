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


def require_str(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    s = value.strip()
    return s if s else None


def require_int(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return None
        try:
            return int(s)
        except ValueError:
            return None
    return None


def require_float(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return None
        try:
            return float(s)
        except ValueError:
            return None
    return None
