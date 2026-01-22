import os

from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]

load_dotenv()

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
if not AUTH0_DOMAIN:
    raise RuntimeError("Missing required environment variable: AUTH0_DOMAIN")

CLIENT_ID = os.getenv("CLIENT_ID")
if not CLIENT_ID:
    raise RuntimeError("Missing required environment variable: CLIENT_ID")

CLIENT_SECRET = os.getenv("CLIENT_SECRET")
if not CLIENT_SECRET:
    raise RuntimeError("Missing required environment variable: CLIENT_SECRET")

AUDIENCE = os.getenv("AUDIENCE")
DEFAULT_SCOPE = os.getenv("SCOPE", "openid profile email")

CORS_ALLOW_ORIGIN = os.getenv("CORS_ALLOW_ORIGIN", "*")

REDIRECT_URI = os.getenv("REDIRECT_URI")
POST_LOGIN_REDIRECT_URL = os.getenv("POST_LOGIN_REDIRECT_URL")
POST_LOGOUT_REDIRECT_URL = os.getenv("POST_LOGOUT_REDIRECT_URL")

COOKIE_SECRET = os.getenv("COOKIE_SECRET", "dev-insecure-change-me-please").encode(
    "utf-8"
)

# Optional: Auth0 Management API (used to resolve the real "connection" name like
# "username-password-authentication" vs "google-oauth2").
#
# If unset, auth-service will fall back to best-effort inference from `userinfo.sub`.
AUTH0_MGMT_CLIENT_ID = os.getenv("AUTH0_MGMT_CLIENT_ID")
AUTH0_MGMT_CLIENT_SECRET = os.getenv("AUTH0_MGMT_CLIENT_SECRET")
AUTH0_MGMT_AUDIENCE = os.getenv(
    "AUTH0_MGMT_AUDIENCE", f"https://{AUTH0_DOMAIN}/api/v2/"
)
AUTH0_MGMT_SCOPE = os.getenv("AUTH0_MGMT_SCOPE", "read:users")
