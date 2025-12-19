import asyncio
import sqlite3
from aiohttp import web

from db import init_db

from helpers import user_repo
from helpers.http import (
    json_error,
    json_ok,
    normalize_email,
    require_str,
    sqlite_error_response,
)
from helpers.settings import db_path as get_db_path, server_host, server_port

from logging_setup import logging_setup

logger = logging_setup.get_logger()

from dotenv import load_dotenv

load_dotenv()


async def _init_db(app: web.Application) -> None:
    path = get_db_path()
    logger.info("Initializing SQLite DB at %s", path)
    try:
        await asyncio.to_thread(init_db, path, reset=False)
    except RuntimeError as e:
        logger.warning("DB init failed (%s). Recreating users table.", e)
        await asyncio.to_thread(
            init_db, path, reset=True
        )  # ako schema nije ista kao očekivana, dropa i rekreira tablicu


async def health(_: web.Request) -> web.Response:
    return json_ok(
        {
            "status": "user-service REST API Server is running just fine. Not sure about the microservice itself."
        }
    )


async def list_users(request: web.Request) -> web.Response:
    logger.info("Listing users from request url: %s", request.url)
    try:
        async with request.app["db_lock"]:
            users = await asyncio.to_thread(user_repo.list_users, get_db_path())
        return json_ok({"users": users})
    except sqlite3.OperationalError as e:
        return sqlite_error_response(logger, action="listing users", err=e)


async def create_user(request: web.Request) -> web.Response:
    logger.info(f"Received request to create a new user from {request.url}.")
    try:
        data = await request.json()
    except Exception:
        return json_error("invalid_json", status=400)

    email = normalize_email(data.get("email"))
    connection = require_str(data.get("connection"))

    if email is None or connection is None:
        return json_error("missing_fields", status=400)

    try:
        async with request.app["db_lock"]:
            created, user_id = await asyncio.to_thread(
                user_repo.ensure_user, get_db_path(), email=email, connection=connection
            )
        logger.info(f"User created: {created}, ID: {user_id}")
        return json_ok({"created": created, "id": user_id})
    except sqlite3.OperationalError as e:
        return sqlite_error_response(logger, action="ensuring user", err=e)
    except Exception as e:
        logger.exception("Unexpected error while ensuring user: %s", e)
        return json_error("internal_error", status=500)


def create_app() -> web.Application:
    app = web.Application()
    app["db_lock"] = asyncio.Lock()
    app.on_startup.append(_init_db)
    app.router.add_get("/health", health)
    app.router.add_get("/users", list_users)
    app.router.add_post("/users", create_user)
    return app


async def start_server(
    app: web.Application, host: str | None, port: int
) -> web.AppRunner:
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=host, port=port)
    await site.start()
    return runner


async def main() -> None:
    host = server_host()
    port = server_port()
    logger.info("Starting user-service aiohttp server on %s:%s", host, port)

    runner: web.AppRunner | None = None
    try:
        runner = await start_server(create_app(), host=host, port=port)
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        raise
    finally:
        if runner is not None:
            await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
