from __future__ import annotations

import os
from typing import Any

import aiohttp
from dotenv import load_dotenv

from logging_setup import logging_setup

logger = logging_setup.get_logger()
load_dotenv()


def _infobip_base_url() -> str | None:

    base_url = (
        (os.getenv("INFOBIP_API_BASE_URL") or "").strip()
    )
    if base_url:
        if not base_url.startswith(("http://", "https://")):
            base_url = f"https://{base_url}"
        return base_url.rstrip("/")


def _infobip_authorization_header() -> str | None:

    api_key = (os.getenv("INFOBIP_API_KEY") or "").strip()
    if not api_key:
        return None

    prefix = (os.getenv("INFOBIP_API_KEY_PREFIX") or "App").strip()
    return f"{prefix} {api_key}"


def _infobip_sender() -> str | None:
    sender = (os.getenv("INFOBIP_SMS_SENDER") or "").strip()
    return sender or None


async def send_sms(*, to_number: str, text: str, logger: Any | None = None) -> dict[str, object]:

    log = logger or globals().get("logger")

    base_url = _infobip_base_url()
    auth = _infobip_authorization_header()
    sender = _infobip_sender()

    if not base_url or not auth or not sender:
        raise RuntimeError(
            "Infobip SMS not configured. Set INFOBIP_API_BASE_URL "
            "INFOBIP_AUTHORIZATION (or INFOBIP_API_KEY), and INFOBIP_SMS_SENDER."
        )

    to_number = (to_number or "").strip().replace(" ", "")
    if not to_number:
        raise ValueError("missing_to_number")

    url = f"{base_url}/messages-api/1/messages"
    payload = {
        "messages": [
            {
                "channel": "SMS",
                "sender": sender,
                "destinations": [{"to": to_number}],
                "content": {"body": {"text": text, "type": "TEXT"}},
            }
        ]
    }
    headers = {
        "Authorization": auth,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            body_text = await resp.text()
            if log:
                if resp.status >= 400:
                    log.warning("Infobip SMS failed (status=%s): %s", resp.status, body_text)
                else:
                    log.info("Infobip SMS sent (status=%s)", resp.status)
            return {"status": resp.status, "body": body_text}


async def send_order_created_sms(*, order: dict[str, object], logger: Any) -> None:
    to_override = (os.getenv("INFOBIP_SMS_TO_OVERRIDE") or "").strip()
    order_phone = str(order.get("phone_number") or "").strip()
    to_number = (to_override or order_phone).replace(" ", "")
    if not to_number:
        logger.warning(
            "Infobip SMS skipped: missing destination number for order_id=%s", order.get("id")
        )
        return

    order_id = str(order.get("id") or "")
    items_value = order.get("items")

    parts: list[str] = []
    if isinstance(items_value, list) and items_value:
        normalized: list[tuple[str, str]] = []
        for it in items_value:
            if not isinstance(it, dict):
                continue
            iid = str(it.get("item_id") or "").strip()
            qty = str(it.get("ordered_quantity") or "").strip()
            if iid and qty:
                normalized.append((iid, qty))

        for iid, qty in normalized[:3]:
            parts.append(f"{iid} x{qty}")
        if len(normalized) > 3:
            parts.append(f"+{len(normalized) - 3} more")

        items_text = ", ".join(parts) if parts else "items"
        text = f"Narudžba {order_id} potvrđena. {len(normalized)} stavka(ke): {items_text}. Hvala Vam na kupnji! #RS-E-commerceApp"
    else:
        item_id = str(order.get("item_id") or "")
        qty = str(order.get("ordered_quantity") or "")
        text = f"Narudžba {order_id} potvrđena. Stavka: {item_id} x{qty}. Hvala Vam na kupnji! #RS-E-commerceApp"

    try:
        await send_sms(to_number=to_number, text=text, logger=logger)
    except Exception as e:
        logger.exception("Infobip SMS error for order_id=%s: %s", order_id, e)
