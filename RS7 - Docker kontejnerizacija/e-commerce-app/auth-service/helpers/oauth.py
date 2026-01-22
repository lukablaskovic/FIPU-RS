import base64
import hashlib
import hmac
import secrets

from aiohttp import web

from .settings import AUTH0_DOMAIN, COOKIE_SECRET, REDIRECT_URI


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def sign(value: str) -> str:
    sig = hmac.new(COOKIE_SECRET, value.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{value}.{sig}"


def unsign(signed_value: str) -> str | None:
    try:
        value, sig = signed_value.rsplit(".", 1)
    except ValueError:
        return None

    expected = hmac.new(
        COOKIE_SECRET, value.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(sig, expected):
        return None

    return value


def set_signed_cookie(
    resp: web.StreamResponse,
    name: str,
    value: str,
    *,
    max_age_s: int = 600,
) -> None:
    resp.set_cookie(
        name,
        sign(value),
        max_age=max_age_s,
        httponly=True,
        samesite="Lax",
        secure=False,
        path="/",
    )


def get_signed_cookie(request: web.Request, name: str) -> str | None:
    raw = request.cookies.get(name)
    if not raw:
        return None
    return unsign(raw)


def pkce_verifier() -> str:
    return secrets.token_urlsafe(64)[:96]


def pkce_challenge(verifier: str) -> str:
    return b64url(hashlib.sha256(verifier.encode("utf-8")).digest())


def resolve_redirect_uri(request: web.Request) -> str:
    if REDIRECT_URI:
        return REDIRECT_URI
    return str(request.url.with_path("/callback").with_query({}).with_fragment(""))


def auth0_authorize_url() -> str:
    return f"https://{AUTH0_DOMAIN}/authorize"


def auth0_token_url() -> str:
    return f"https://{AUTH0_DOMAIN}/oauth/token"


def auth0_userinfo_url() -> str:
    return f"https://{AUTH0_DOMAIN}/userinfo"


def auth0_logout_url() -> str:
    return f"https://{AUTH0_DOMAIN}/v2/logout"
