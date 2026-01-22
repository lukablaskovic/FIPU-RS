import asyncio
import sqlite3

import aiohttp
from aiohttp import web
from dotenv import load_dotenv

from db import init_db
from helpers import order_repo
from helpers.infobip_sms import send_order_created_sms, send_sms
from helpers.http import (
    json_error,
    json_ok,
    normalize_email,
    require_int,
    require_str,
    sqlite_error_response,
)
from helpers.settings import (
    catalog_service_base_url,
    db_path as get_db_path,
    server_host,
    server_port,
)
from logging_setup import logging_setup
from websocket_handlers import register_ws_routes


logger = logging_setup.get_logger()
load_dotenv()


# background task scheduler helper fun
def _schedule_bg_task(app: web.Application, coro: object) -> None:

    task = asyncio.create_task(coro)
    tasks: set[asyncio.Task] = app["bg_tasks"]
    tasks.add(task)
    task.add_done_callback(tasks.discard)


async def _cancel_bg_tasks(app: web.Application) -> None:
    tasks: set[asyncio.Task] = app.get("bg_tasks", set())
    for t in list(tasks):
        t.cancel()
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)


async def _init_db(app: web.Application) -> None:
    path = get_db_path()
    logger.info("Initializing SQLite DB at %s", path)
    try:
        await asyncio.to_thread(init_db, path, reset=False)
    except RuntimeError as e:
        logger.warning("DB init failed (%s). Recreating orders table.", e)
        await asyncio.to_thread(init_db, path, reset=True)


async def _init_http_session(app: web.Application) -> None:
    timeout = aiohttp.ClientTimeout(total=10)
    app["http_session"] = aiohttp.ClientSession(timeout=timeout)


async def _close_http_session(app: web.Application) -> None:
    session: aiohttp.ClientSession | None = app.get("http_session")
    if session is not None:
        await session.close()


async def health(_: web.Request) -> web.Response:
    return json_ok({"status": "order-service REST API Server is running just fine."})


# --------


# Ovo je sve jako natrpano i nezgrapno, na sreću, radit ćemo Pydantic kasnije
# Ručne validacije su naporne i sklone greškama - Pydantic predstavlja model-based pristup validaciji koji je puno elegantnije rješenje
def _parse_order_payload(data: dict) -> tuple[dict[str, object] | None, str | None]:
    user_id = require_str(data.get("user_id"))
    name = require_str(data.get("name"))
    surname = require_str(data.get("surname"))
    delivery_address = require_str(data.get("delivery_address"))
    phone_number = require_str(data.get("phone_number"))
    email_address = normalize_email(data.get("email_address"))
    client_request_id = require_str(data.get("client_request_id"))
    send_sms_raw = data.get("send_sms")
    send_sms = bool(send_sms_raw) if isinstance(send_sms_raw, bool) else False

    if user_id is None or name is None or surname is None or delivery_address is None:
        return None, "missing_fields"
    if phone_number is None or email_address is None:
        return None, "missing_fields"

    items_value = data.get("items")
    items: list[dict[str, object]] = []

    if isinstance(items_value, list):
        for it in items_value:
            if not isinstance(it, dict):
                return None, "invalid_items"
            item_id = require_str(it.get("item_id"))
            ordered_quantity = require_int(it.get("ordered_quantity"))
            if item_id is None or ordered_quantity is None or ordered_quantity <= 0:
                return None, "invalid_items"
            items.append({"item_id": item_id, "ordered_quantity": ordered_quantity})
    else:
        item_id = require_str(data.get("item_id"))
        ordered_quantity = require_int(data.get("ordered_quantity"))
        if item_id is None or ordered_quantity is None or ordered_quantity <= 0:
            return None, "missing_fields"
        items = [{"item_id": item_id, "ordered_quantity": ordered_quantity}]

    return {
        "user_id": user_id,
        "items": items,
        "name": name,
        "surname": surname,
        "delivery_address": delivery_address,
        "phone_number": phone_number,
        "email_address": email_address,
        "client_request_id": client_request_id,
        "send_sms": send_sms,
    }, None


async def _catalog_post_json(
    request: web.Request, *, path: str, payload: dict[str, object]
) -> tuple[int, dict[str, object] | None]:
    base = catalog_service_base_url()
    url = f"{base}{path}"
    session: aiohttp.ClientSession = request.app["http_session"]
    async with session.post(url, json=payload) as resp:
        content_type = resp.headers.get("Content-Type", "")
        raw_text: str | None = None
        try:
            data = await resp.json()
        except Exception:
            # If catalog returns HTML/text (wrong URL/proxy/etc), surface that to the caller
            # so frontend has actionable diagnostics instead of `catalog: null`.
            try:
                raw_text = await resp.text()
            except Exception:
                raw_text = None
            logger.warning(
                "Catalog response not JSON: url=%s status=%s content_type=%s body=%s",
                url,
                resp.status,
                content_type,
                (raw_text[:500] if isinstance(raw_text, str) else None),
            )
            data = {
                "ok": False,
                "error": "non_json_response",
                "url": url,
                "status": resp.status,
                "content_type": content_type,
                "body": raw_text,
            }
        return resp.status, data


# POST /orders
async def create_order(request: web.Request) -> web.Response:
    logger.info("Creating a new order from request url: %s", request.url)
    try:
        data = await request.json()
    except Exception:
        return json_error("invalid_json", status=400)

    payload, err = _parse_order_payload(data)
    if err is not None or payload is None:
        return json_error(err or "missing_fields", status=400)

    try:
        status, check = await _catalog_post_json(
            request,
            path="/inventory/check",
            payload={"items": list(payload["items"])},  # type: ignore[arg-type]
        )
        if status != 200 or not isinstance(check, dict) or not bool(check.get("ok")):
            return web.json_response(
                {"error": "items_unavailable", "catalog": check}, status=409
            )

        async with request.app["db_lock"]:
            order, created = await asyncio.to_thread(
                order_repo.create_order,
                get_db_path(),
                user_id=str(payload["user_id"]),
                items=list(payload["items"]),  # type: ignore[arg-type]
                name=str(payload["name"]),
                surname=str(payload["surname"]),
                delivery_address=str(payload["delivery_address"]),
                phone_number=str(payload["phone_number"]),
                email_address=str(payload["email_address"]),
                client_request_id=(
                    str(payload["client_request_id"])
                    if payload.get("client_request_id")
                    else None
                ),
            )
        if created:
            dec_status, dec = await _catalog_post_json(
                request,
                path="/inventory/decrement",
                payload={"items": list(payload["items"])},  # type: ignore[arg-type]
            )
            if dec_status != 200:
                async with request.app["db_lock"]:
                    await asyncio.to_thread(
                        order_repo.delete_order,
                        get_db_path(),
                        order_id=str(order["id"]),
                    )
                return web.json_response(
                    {"error": "catalog_decrement_failed", "catalog": dec}, status=409
                )

            if bool(payload.get("send_sms")):
                _schedule_bg_task(
                    request.app, send_order_created_sms(order=order, logger=logger)
                )
        return json_ok(
            {"created": bool(created), "id": order["id"], "order": order},
            status=(201 if created else 200),
        )
    except sqlite3.OperationalError as e:
        return sqlite_error_response(logger, action="creating order", err=e)
    except Exception as e:
        logger.exception("Unexpected error while creating order: %s", e)
        return json_error("internal_error", status=500)


# GET /orders
async def list_orders(request: web.Request) -> web.Response:
    logger.info("Listing orders from request url: %s", request.url)
    try:
        async with request.app["db_lock"]:
            orders = await asyncio.to_thread(order_repo.list_orders, get_db_path())
        return json_ok({"orders": orders})
    except sqlite3.OperationalError as e:
        return sqlite_error_response(logger, action="listing orders", err=e)


# GET /orders/{id}
async def get_order(request: web.Request) -> web.Response:
    logger.info("Getting an order from request url: %s", request.url)
    order_id = request.match_info.get("id")
    if not order_id:
        return json_error("missing_id", status=400)

    try:
        async with request.app["db_lock"]:
            order = await asyncio.to_thread(
                order_repo.get_order, get_db_path(), order_id=order_id
            )
        if order is None:
            return json_error("not_found", status=404)
        return json_ok({"order": order})
    except sqlite3.OperationalError as e:
        return sqlite_error_response(logger, action="getting order", err=e)


# GET /orders/user/{user_id}
async def list_orders_by_user(request: web.Request) -> web.Response:
    logger.info("Listing orders by user from request url: %s", request.url)
    user_id = request.match_info.get("user_id")
    if not user_id:
        return json_error("missing_user_id", status=400)

    try:
        async with request.app["db_lock"]:
            orders = await asyncio.to_thread(
                order_repo.list_orders_by_user_id, get_db_path(), user_id=user_id
            )
        return json_ok({"orders": orders})
    except sqlite3.OperationalError as e:
        return sqlite_error_response(logger, action="listing orders by user", err=e)


# DELETE /clear
async def clear_all_orders(request: web.Request) -> web.Response:
    logger.warning("Clearing ALL orders from request url: %s", request.url)
    try:
        async with request.app["db_lock"]:
            result = await asyncio.to_thread(order_repo.clear_orders, get_db_path())
        return json_ok({"cleared": True, **result})
    except sqlite3.OperationalError as e:
        return sqlite_error_response(logger, action="clearing orders", err=e)
    except Exception as e:
        logger.exception("Unexpected error while clearing orders: %s", e)
        return json_error("internal_error", status=500)


# POST /sms-test/{number}
async def sms_test(request: web.Request) -> web.Response:
    logger.info("Sending SMS test from request url: %s", request.url)
    number = request.match_info.get("number")
    if not number:
        return json_error("missing_number", status=400)

    text = "Hi there! This is SMS test from order-service using Infobip Messages API."
    try:
        result = await send_sms(to_number=number, text=text, logger=logger)
        return json_ok({"ok": True, "to": number, "result": result})
    except Exception as e:
        logger.exception("SMS test failed: %s", e)
        return json_error("sms_test_failed", status=500)


def create_app() -> web.Application:
    app = web.Application()
    app["db_lock"] = asyncio.Lock()
    app["bg_tasks"] = set()
    app.on_startup.append(_init_db)
    app.on_startup.append(_init_http_session)
    app.on_cleanup.append(_cancel_bg_tasks)
    app.on_cleanup.append(_close_http_session)

    app.router.add_get("/health", health)
    app.router.add_post("/sms-test/{number}", sms_test)
    app.router.add_delete("/clear", clear_all_orders)
    app.router.add_get("/orders", list_orders)
    app.router.add_get("/orders/user/{user_id}", list_orders_by_user)
    app.router.add_get("/orders/{id}", get_order)
    app.router.add_post("/orders", create_order)
    register_ws_routes(app)

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
    logger.info("Starting order-service aiohttp server on %s:%s", host, port)

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
