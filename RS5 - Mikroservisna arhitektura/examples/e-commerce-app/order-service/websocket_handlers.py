from __future__ import annotations

import asyncio
import random
from datetime import datetime, timezone

from aiohttp import WSCloseCode, web

from logging_setup import logging_setup


logger = logging_setup.get_logger()


def _random_timestamp_iso() -> str:
    now = datetime.now(timezone.utc).astimezone()
    ms = random.randint(0, 999)
    return now.replace(microsecond=ms * 1000).isoformat(timespec="milliseconds")


async def _ws_send_tracking_event(
    ws: web.WebSocketResponse,
    *,
    order_id: str | None,
    step: int,
    text: str,
    kind: str = "status",
) -> None:
    if ws.closed:
        return
    await ws.send_json(
        {
            "type": "order_tracking",
            "kind": kind,  # status | done
            "order_id": order_id,
            "step": step,
            "text": text,
            "timestamp": _random_timestamp_iso(),
        }
    )


async def _ws_order_tracking_simulation(ws: web.WebSocketResponse, *, order_id: str | None) -> None:
    await _ws_send_tracking_event(ws, order_id=order_id, step=1, text="Pakiramo tvoju narudžbu…")
    await asyncio.sleep(5)

    await _ws_send_tracking_event(ws, order_id=order_id, step=2, text="Pickup dostavne službe")
    await asyncio.sleep(10)

    await _ws_send_tracking_event(ws, order_id=order_id, step=3, text="Tvoja narudžba je na dostavi…")
    await asyncio.sleep(10)

    await _ws_send_tracking_event(
        ws,
        order_id=order_id,
        step=4,
        text="Narudžba dostavljena! Uživaj!",
        kind="done",
    )

    await asyncio.sleep(0.5)
    if not ws.closed:
        await ws.close(code=WSCloseCode.OK, message=b"tracking_done")


async def ws_track_order(request: web.Request) -> web.StreamResponse:
    order_id = request.match_info.get("id")
    ws = web.WebSocketResponse(heartbeat=20.0)
    await ws.prepare(request)

    logger.info("WebSocket tracking activated for order_id=%s from %s", order_id, request.remote)

    sim_task = asyncio.create_task(_ws_order_tracking_simulation(ws, order_id=order_id))
    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                logger.info("WS message order_id=%s: %s", order_id, msg.data)
                if str(msg.data).strip().lower() in {"stop", "close", "cancel"}:
                    await ws.close(code=WSCloseCode.OK, message=b"client_closed")
            elif msg.type == web.WSMsgType.ERROR:
                logger.warning("WS error order_id=%s: %s", order_id, ws.exception())
    finally:
        if not sim_task.done():
            sim_task.cancel()
            await asyncio.gather(sim_task, return_exceptions=True)
        logger.info("WebSocket tracking closed for order_id=%s", order_id)

    return ws


def register_ws_routes(app: web.Application) -> None:
    app.router.add_get("/ws/orders/{id}", ws_track_order)
