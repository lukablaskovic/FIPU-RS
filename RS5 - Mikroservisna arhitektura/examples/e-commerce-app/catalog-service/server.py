from __future__ import annotations

import asyncio
import sqlite3

from aiohttp import web
from dotenv import load_dotenv

from db import init_db
from helpers import product_repo
from helpers.http import (
    json_error,
    json_ok,
    require_float,
    require_int,
    require_str,
    sqlite_error_response,
)
from helpers.settings import db_path as get_db_path, server_host, server_port
from logging_setup import logging_setup


logger = logging_setup.get_logger()
load_dotenv()


async def _init_db(app: web.Application) -> None:
    path = get_db_path()
    logger.info("Initializing SQLite DB at %s", path)
    try:
        await asyncio.to_thread(init_db, path, reset=False)
    except RuntimeError as e:
        logger.warning("DB init failed (%s). Recreating products table.", e)
        await asyncio.to_thread(init_db, path, reset=True)


async def health(_: web.Request) -> web.Response:
    return json_ok({"status": "catalog-service REST API Server is running just fine. Not sure about the microservice itself."})


async def list_products(request: web.Request) -> web.Response:
    logger.info("Listing products from request url: %s", request.url)
    try:
        async with request.app["db_lock"]:
            products = await asyncio.to_thread(product_repo.list_products, get_db_path())
        return json_ok({"products": products})
    except sqlite3.OperationalError as e:
        return sqlite_error_response(logger, action="listing products", err=e)


async def get_product(request: web.Request) -> web.Response:
    logger.info("Getting a product from request url: %s", request.url)
    product_id = request.match_info.get("id")
    if not product_id:
        return json_error("missing_id", status=400)

    try:
        async with request.app["db_lock"]:
            product = await asyncio.to_thread(
                product_repo.get_product, get_db_path(), product_id=product_id
            )
        if product is None:
            return json_error("not_found", status=404)
        return json_ok({"product": product})
    except sqlite3.OperationalError as e:
        return sqlite_error_response(logger, action="getting product", err=e)


def _parse_product_payload(data: dict, *, allow_partial: bool) -> tuple[dict[str, object] | None, str | None]:
    name = require_str(data.get("name"))
    category = require_str(data.get("category"))
    price = require_float(data.get("price"))
    currency = require_str(data.get("currency"))
    description = require_str(data.get("description"))
    shipping_time = require_str(data.get("shipping_time"))
    amount_available = require_int(data.get("amount_available"))
    public_image_url = require_str(data.get("public_image_url"))

    if allow_partial:
        updates: dict[str, object] = {}
        if name is not None:
            updates["name"] = name
        if category is not None:
            updates["category"] = category
        if price is not None:
            updates["price"] = price
        if currency is not None:
            updates["currency"] = currency
        if description is not None:
            updates["description"] = description
        if shipping_time is not None:
            updates["shipping_time"] = shipping_time
        if amount_available is not None:
            updates["amount_available"] = amount_available
        if public_image_url is not None:
            updates["public_image_url"] = public_image_url

        if not updates:
            return None, "missing_fields"
        return updates, None

    if (
        name is None
        or category is None
        or price is None
        or currency is None
        or description is None
        or shipping_time is None
        or amount_available is None
        or public_image_url is None
    ):
        return None, "missing_fields"

    return {
        "name": name,
        "category": category,
        "price": price,
        "currency": currency,
        "description": description,
        "shipping_time": shipping_time,
        "amount_available": amount_available,
        "public_image_url": public_image_url,
    }, None


async def create_product(request: web.Request) -> web.Response:
    logger.info("Creating a new product from request url: %s", request.url)
    try:
        data = await request.json()
    except Exception:
        return json_error("invalid_json", status=400)

    payload, err = _parse_product_payload(data, allow_partial=False)
    if err is not None or payload is None:
        return json_error(err or "missing_fields", status=400)

    try:
        async with request.app["db_lock"]:
            product_id = await asyncio.to_thread(
                product_repo.create_product,
                get_db_path(),
                name=str(payload["name"]),
                category=str(payload["category"]),
                price=float(payload["price"]),
                currency=str(payload["currency"]),
                description=str(payload["description"]),
                shipping_time=str(payload["shipping_time"]),
                amount_available=int(payload["amount_available"]),
                public_image_url=str(payload["public_image_url"]),
            )
        return json_ok({"created": True, "id": product_id}, status=201)
    except sqlite3.OperationalError as e:
        return sqlite_error_response(logger, action="creating product", err=e)
    except Exception as e:
        logger.exception("Unexpected error while creating product: %s", e)
        return json_error("internal_error", status=500)


async def update_product(request: web.Request) -> web.Response:
    logger.info("Updating a product from request url: %s", request.url)
    product_id = request.match_info.get("id")
    if not product_id:
        return json_error("missing_id", status=400)

    try:
        data = await request.json()
    except Exception:
        return json_error("invalid_json", status=400)

    updates, err = _parse_product_payload(data, allow_partial=True)
    if err is not None or updates is None:
        return json_error(err or "missing_fields", status=400)

    try:
        async with request.app["db_lock"]:
            current = await asyncio.to_thread(
                product_repo.get_product, get_db_path(), product_id=product_id
            )
            if current is None:
                return json_error("not_found", status=404)

            merged = {**current, **updates}
            ok = await asyncio.to_thread(
                product_repo.update_product,
                get_db_path(),
                product_id=product_id,
                name=str(merged["name"]),
                category=str(merged["category"]),
                price=float(merged["price"]),
                currency=str(merged["currency"]),
                description=str(merged["description"]),
                shipping_time=str(merged["shipping_time"]),
                amount_available=int(merged["amount_available"]),
                public_image_url=str(merged["public_image_url"]),
            )

        if not ok:
            return json_error("not_found", status=404)
        return json_ok({"updated": True})
    except sqlite3.OperationalError as e:
        return sqlite_error_response(logger, action="updating product", err=e)
    except Exception as e:
        logger.exception("Unexpected error while updating product: %s", e)
        return json_error("internal_error", status=500)


async def delete_product(request: web.Request) -> web.Response:
    logger.info("Deleting a product from request url: %s", request.url)
    product_id = request.match_info.get("id")
    if not product_id:
        return json_error("missing_id", status=400)

    try:
        async with request.app["db_lock"]:
            deleted = await asyncio.to_thread(
                product_repo.delete_product, get_db_path(), product_id=product_id
            )
        if not deleted:
            return json_error("not_found", status=404)
        return json_ok({"deleted": True})
    except sqlite3.OperationalError as e:
        return sqlite_error_response(logger, action="deleting product", err=e)


async def clear_products(request: web.Request) -> web.Response:
    logger.warning("Clearing ALL products from request url: %s", request.url)
    try:
        async with request.app["db_lock"]:
            deleted = await asyncio.to_thread(product_repo.clear_products, get_db_path())
        return json_ok({"cleared": True, "deleted": deleted})
    except sqlite3.OperationalError as e:
        return sqlite_error_response(logger, action="clearing products", err=e)


def _parse_inventory_items(data: dict) -> tuple[list[tuple[str, int]] | None, str | None]:
    items_value = data.get("items")
    if not isinstance(items_value, list) or not items_value:
        return None, "missing_items"

    items: list[tuple[str, int]] = []
    for it in items_value:
        if not isinstance(it, dict):
            return None, "invalid_items"
        item_id = require_str(it.get("item_id"))
        qty = require_int(it.get("ordered_quantity"))
        if item_id is None or qty is None or qty <= 0:
            return None, "invalid_items"
        items.append((item_id, int(qty)))

    return items, None


async def inventory_check(request: web.Request) -> web.Response:
    logger.info("Inventory check from request url: %s", request.url)
    try:
        data = await request.json()
    except Exception:
        return json_error("invalid_json", status=400)

    items, err = _parse_inventory_items(data if isinstance(data, dict) else {})
    if err is not None or items is None:
        return json_error(err or "missing_items", status=400)

    try:
        async with request.app["db_lock"]:
            result = await asyncio.to_thread(product_repo.check_availability, get_db_path(), items=items)
        return json_ok(result)
    except sqlite3.OperationalError as e:
        return sqlite_error_response(logger, action="checking inventory", err=e)


async def inventory_decrement(request: web.Request) -> web.Response:
    logger.info("Inventory decrement from request url: %s", request.url)
    try:
        data = await request.json()
    except Exception:
        return json_error("invalid_json", status=400)

    items, err = _parse_inventory_items(data if isinstance(data, dict) else {})
    if err is not None or items is None:
        return json_error(err or "missing_items", status=400)

    try:
        async with request.app["db_lock"]:
            result = await asyncio.to_thread(product_repo.decrement_stock, get_db_path(), items=items)
        if not bool(result.get("ok")):
            return web.json_response({"error": "insufficient_stock", **result}, status=409)
        return json_ok(result)
    except sqlite3.OperationalError as e:
        return sqlite_error_response(logger, action="decrementing inventory", err=e)


def create_app() -> web.Application:
    app = web.Application()
    app["db_lock"] = asyncio.Lock()
    app.on_startup.append(_init_db)

    app.router.add_get("/health", health)

    app.router.add_get("/products", list_products)
    app.router.add_post("/products", create_product)
    app.router.add_get("/products/{id}", get_product)
    app.router.add_put("/products/{id}", update_product)
    app.router.add_delete("/products/{id}", delete_product)
    app.router.add_delete("/clear", clear_products)
    app.router.add_post("/inventory/check", inventory_check)
    app.router.add_post("/inventory/decrement", inventory_decrement)

    return app


async def start_server(app: web.Application, host: str | None, port: int) -> web.AppRunner:
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=host, port=port)
    await site.start()
    return runner


async def main() -> None:
    host = server_host()
    port = server_port()
    logger.info("Starting catalog-service aiohttp server on %s:%s", host, port)

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
