import os
from pathlib import Path

from db import DEFAULT_DB_PATH


def db_path() -> Path:
    return Path(os.getenv("ORDER_DB_PATH", str(DEFAULT_DB_PATH))).expanduser().resolve()


def server_host() -> str | None:
    return os.getenv("SERVER_HOST")


def server_port() -> int:
    return int(os.getenv("SERVER_PORT", "8003"))


def catalog_service_base_url() -> str:
    return (os.getenv("CATALOG_SERVICE_BASE_URL")).rstrip("/")
