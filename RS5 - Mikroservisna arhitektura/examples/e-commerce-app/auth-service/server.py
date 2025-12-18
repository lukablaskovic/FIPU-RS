from __future__ import annotations

import asyncio
import json
import os
import time
from typing import Any
from urllib.parse import quote

from aiohttp import ClientSession, ClientTimeout, web
from authlib.integrations.requests_client import OAuth2Session

from helpers.middleware import cors_middleware
from helpers.oauth import (
    auth0_authorize_url,
    auth0_logout_url,
    auth0_token_url,
    auth0_userinfo_url,
    b64url,
    get_signed_cookie,
    pkce_challenge,
    pkce_verifier,
    resolve_redirect_uri,
    set_signed_cookie,
)
from helpers.settings import (
    AUDIENCE,
    AUTH0_DOMAIN,
    AUTH0_MGMT_AUDIENCE,
    AUTH0_MGMT_CLIENT_ID,
    AUTH0_MGMT_CLIENT_SECRET,
    AUTH0_MGMT_SCOPE,
    CLIENT_ID,
    CLIENT_SECRET,
    DEFAULT_SCOPE,
    POST_LOGIN_REDIRECT_URL,
    POST_LOGOUT_REDIRECT_URL,
)
from logging_setup import logging_setup

logger = logging_setup.get_logger()

POST_LOGIN_REDIRECT_COOKIE = "post_login_redirect"

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8001")

async def health(_: web.Request) -> web.Response:
    return web.json_response({"status": "auth-service REST API Server is running just fine. Not sure about the microservice itself."})


def _infer_connection_from_sub(sub: str) -> str:
    """
    Best-effort fallback.
    - "google-oauth2|..." -> "google-oauth2"
    - "auth0|..." -> "auth0"  (NOT the real DB connection name)
    """
    if "|" not in sub:
        return "unknown"
    provider = sub.split("|", 1)[0]
    return provider or "unknown"


_mgmt_token_lock = asyncio.Lock()
_mgmt_token_cache: dict[str, Any] = {"access_token": None, "expires_at": 0.0}
_mgmt_warned_missing_creds = False


async def _get_auth0_mgmt_access_token() -> str | None:
    global _mgmt_warned_missing_creds
    if not AUTH0_MGMT_CLIENT_ID or not AUTH0_MGMT_CLIENT_SECRET:
        if not _mgmt_warned_missing_creds:
            _mgmt_warned_missing_creds = True
            logger.warning(
                "Auth0 management API is not configured (missing AUTH0_MGMT_CLIENT_ID/SECRET); "
                "falling back to provider inference from `sub`."
            )
        return None

    now = time.time()
    cached = _mgmt_token_cache.get("access_token")
    expires_at = float(_mgmt_token_cache.get("expires_at") or 0.0)
    if isinstance(cached, str) and cached and expires_at > now + 30:
        return cached

    async with _mgmt_token_lock:
        now = time.time()
        cached = _mgmt_token_cache.get("access_token")
        expires_at = float(_mgmt_token_cache.get("expires_at") or 0.0)
        if isinstance(cached, str) and cached and expires_at > now + 30:
            return cached

        async def _request_token(audience: str) -> dict[str, Any] | None:
            timeout = ClientTimeout(total=5)
            async with ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"https://{AUTH0_DOMAIN}/oauth/token",
                    json={
                        "client_id": AUTH0_MGMT_CLIENT_ID,
                        "client_secret": AUTH0_MGMT_CLIENT_SECRET,
                        "audience": audience,
                        "grant_type": "client_credentials",
                        "scope": AUTH0_MGMT_SCOPE,
                    },
                ) as resp:
                    if resp.status >= 400:
                        body = await resp.text()
                        logger.warning(
                            "Auth0 mgmt token request failed: status=%s audience=%s body=%s",
                            resp.status,
                            audience,
                            body[:500],
                        )
                        return None
                    return await resp.json()

        data = await _request_token(AUTH0_MGMT_AUDIENCE)
        if data is None:
            # Common Auth0 misconfig: trailing slash mismatch on the Mgmt API audience.
            aud = AUTH0_MGMT_AUDIENCE or ""
            if aud.endswith("/"):
                alt = aud.rstrip("/")
            else:
                alt = aud + "/"
            if alt and alt != aud:
                data = await _request_token(alt)
        if data is None:
            return None

        access_token = data.get("access_token")
        if not isinstance(access_token, str) or not access_token:
            return None

        expires_in = data.get("expires_in")
        try:
            expires_in_s = int(expires_in)
        except Exception:
            expires_in_s = 3600

        _mgmt_token_cache["access_token"] = access_token
        _mgmt_token_cache["expires_at"] = time.time() + max(60, expires_in_s)
        return access_token


def _connection_from_identities(sub: str, identities: list[dict[str, Any]]) -> str | None:
    if "|" not in sub:
        return None
    provider, raw_user_id = sub.split("|", 1)
    if not provider or not raw_user_id:
        return None

    for ident in identities:
        if not isinstance(ident, dict):
            continue
        if ident.get("provider") == provider and ident.get("user_id") == raw_user_id:
            conn = ident.get("connection")
            if isinstance(conn, str) and conn:
                return conn

    for ident in identities:
        if not isinstance(ident, dict):
            continue
        conn = ident.get("connection")
        if isinstance(conn, str) and conn:
            return conn

    return None


async def _resolve_auth0_connection(userinfo: dict[str, Any]) -> str:
    sub = userinfo.get("sub")
    if not isinstance(sub, str) or not sub:
        return "unknown"

    mgmt_token = await _get_auth0_mgmt_access_token()
    if not mgmt_token:
        conn = _infer_connection_from_sub(sub)
        logger.info("Resolved connection via fallback: sub=%s connection=%s", sub, conn)
        return conn

    try:
        timeout = ClientTimeout(total=5)
        async with ClientSession(timeout=timeout) as session:
            async with session.get(
                f"https://{AUTH0_DOMAIN}/api/v2/users/{quote(sub, safe='')}",
                headers={"Authorization": f"Bearer {mgmt_token}"},
                params={"fields": "identities", "include_fields": "true"},
            ) as resp:
                if resp.status >= 400:
                    body = await resp.text()
                    logger.warning("Auth0 mgmt user lookup failed: status=%s body=%s", resp.status, body[:500])
                    conn = _infer_connection_from_sub(sub)
                    logger.info("Resolved connection via fallback: sub=%s connection=%s", sub, conn)
                    return conn
                data = await resp.json()

        identities = data.get("identities")
        if isinstance(identities, list):
            conn = _connection_from_identities(sub, identities)
            if conn:
                logger.info("Resolved connection via Auth0 mgmt API: sub=%s connection=%s", sub, conn)
                return conn
    except Exception as e:
        logger.warning("Auth0 mgmt user lookup errored: %s", e)

    conn = _infer_connection_from_sub(sub)
    logger.info("Resolved connection via fallback: sub=%s connection=%s", sub, conn)
    return conn

def _userinfo_to_user_payload(userinfo: dict[str, Any]) -> dict[str, str] | None:
    sub = userinfo.get("sub")
    if not isinstance(sub, str) or not sub:
        return None

    connection = _infer_connection_from_sub(sub)

    email = userinfo.get("email")
    if not isinstance(email, str) or not email.strip():
        return None

    return {"email": email.strip().lower(), "connection": connection}


async def login(request: web.Request) -> web.StreamResponse: # StreamResponse je lower-level response object za aiohttp, web.Response je nadklasa StreamResponse klase
    logger.info(f"Login request received from {request.url}")
    redirect_uri = resolve_redirect_uri(request)

    next_url = request.rel_url.query.get("next")

    verifier = pkce_verifier()
    logger.debug(f"PKCE verifier: {verifier}")
    challenge = pkce_challenge(verifier)
    logger.debug(f"PKCE challenge: {challenge}")

    oauth = OAuth2Session(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scope=DEFAULT_SCOPE,
        redirect_uri=redirect_uri,
    )

    extra: dict[str, Any] = {}
    if AUDIENCE:
        extra["audience"] = AUDIENCE

    authorization_url, state = oauth.create_authorization_url(
        auth0_authorize_url(),
        code_challenge=challenge,
        code_challenge_method="S256",
        **extra,
    )

    resp = web.HTTPFound(authorization_url) # kao HTTP odgovor se vraća URL za autentifikaciju preko Auth0 servisa.
    set_signed_cookie(resp, "oauth_state", state, max_age_s=600)
    set_signed_cookie(resp, "pkce_verifier", verifier, max_age_s=600)
    if next_url:
        set_signed_cookie(resp, POST_LOGIN_REDIRECT_COOKIE, next_url, max_age_s=900)
    return resp


async def callback(request: web.Request) -> web.StreamResponse:
    logger.info(f"Callback request received from {request.url}")
    code = request.rel_url.query.get("code")
    state = request.rel_url.query.get("state")

    if not code or not state:
        return web.json_response({"error": "missing_code_or_state"}, status=400)

    expected_state = get_signed_cookie(request, "oauth_state")
    if not expected_state or expected_state != state:
        return web.json_response({"error": "invalid_state"}, status=400)

    verifier = get_signed_cookie(request, "pkce_verifier")
    if not verifier:
        return web.json_response({"error": "missing_pkce_verifier"}, status=400)

    redirect_uri = resolve_redirect_uri(request)

    def _exchange() -> tuple[dict[str, Any], dict[str, Any]]:
        oauth = OAuth2Session(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            scope=DEFAULT_SCOPE,
            redirect_uri=redirect_uri,
        )

        token: dict[str, Any] = oauth.fetch_token(
            auth0_token_url(),
            code=code,
            code_verifier=verifier,
        )

        userinfo_resp = oauth.get(auth0_userinfo_url())
        userinfo_resp.raise_for_status()
        userinfo: dict[str, Any] = userinfo_resp.json()

        return token, userinfo

    try:
        token, userinfo = await asyncio.to_thread(_exchange)
    except Exception as e:
        logger.exception("OAuth callback failed: %s", e)
        return web.json_response({"error": "oauth_callback_failed"}, status=502)

    payload = _userinfo_to_user_payload(userinfo)
    if payload is not None:
        payload["connection"] = await _resolve_auth0_connection(userinfo)
        try:
            timeout = ClientTimeout(total=5)
            async with ClientSession(timeout=timeout) as session:
                async with session.post(f"{USER_SERVICE_URL}/users", json=payload) as resp:
                    if resp.status >= 400:
                        body = await resp.text()
                        logger.warning(
                            "user-service ensure failed: status=%s body=%s",
                            resp.status,
                            body[:500],
                        )
        except Exception as e:
            logger.warning("user-service ensure failed: %s", e)

    redirect_to = get_signed_cookie(request, POST_LOGIN_REDIRECT_COOKIE) or POST_LOGIN_REDIRECT_URL

    if redirect_to:
        session_payload = {"token": token, "userinfo": userinfo}
        session_encoded = b64url(json.dumps(session_payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))
        resp = web.HTTPFound(f"{redirect_to}#session={session_encoded}")
        resp.del_cookie("oauth_state", path="/")
        resp.del_cookie("pkce_verifier", path="/")
        resp.del_cookie(POST_LOGIN_REDIRECT_COOKIE, path="/")
        return resp

    resp = web.json_response({"token": token, "userinfo": userinfo})
    resp.del_cookie("oauth_state", path="/")
    resp.del_cookie("pkce_verifier", path="/")
    resp.del_cookie(POST_LOGIN_REDIRECT_COOKIE, path="/")
    return resp


async def logout(request: web.Request) -> web.StreamResponse:
    return_to = request.rel_url.query.get("returnTo") or POST_LOGOUT_REDIRECT_URL
    if not return_to:
        return_to = str(request.url.with_path("/").with_query({}).with_fragment(""))

    url = (
        f"{auth0_logout_url()}"
        f"?client_id={quote(CLIENT_ID or '')}"
        f"&returnTo={quote(return_to)}"
    )

    resp = web.HTTPFound(url)
    resp.del_cookie("oauth_state", path="/")
    resp.del_cookie("pkce_verifier", path="/")
    return resp


def create_app() -> web.Application: # vraća instancu HTTP web poslužitelja s definiranim rutama
    app = web.Application(middlewares=[cors_middleware])
    app.router.add_get("/health", health) # provjeri je li mikroservis živ
    app.router.add_get("/login", login) 
    app.router.add_get("/callback", callback)
    app.router.add_get("/logout", logout)
    app.router.add_route("OPTIONS", "/{tail:.*}", lambda _: web.Response(status=204))
    return app


async def start_server(app: web.Application, host: str, port: int) -> web.AppRunner:
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=host, port=port)
    await site.start()
    return runner

async def main() -> None:
    host = os.getenv("SERVER_HOST")
    port = int(os.getenv("SERVER_PORT", "8000")) # ako SERVER_PORT env nije definiran, koristi 8000

    logger.info(f"Starting auth-service aiohttp server on {host}:{port}")

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
