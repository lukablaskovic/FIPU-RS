from __future__ import annotations

import os
from pathlib import Path

from db import DEFAULT_DB_PATH


def db_path() -> Path:
    return Path(os.getenv("CATALOG_DB_PATH", str(DEFAULT_DB_PATH))).expanduser().resolve()


def server_host() -> str | None:
    return os.getenv("SERVER_HOST")


def server_port() -> int:
    return int(os.getenv("SERVER_PORT", "8002"))
