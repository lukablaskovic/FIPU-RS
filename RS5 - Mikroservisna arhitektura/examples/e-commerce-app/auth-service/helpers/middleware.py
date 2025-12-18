from __future__ import annotations

from aiohttp import web

from .settings import CORS_ALLOW_ORIGIN


@web.middleware
async def cors_middleware(request: web.Request, handler):
    if request.method == "OPTIONS":
        resp = web.Response(status=204)
    else:
        resp = await handler(request)

    resp.headers["Access-Control-Allow-Origin"] = CORS_ALLOW_ORIGIN or "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    resp.headers["Access-Control-Max-Age"] = "86400"
    return resp
