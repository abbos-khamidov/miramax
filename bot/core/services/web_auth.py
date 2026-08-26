"""Login/password auth for the standalone (non-Telegram) analytics page.

Separate from core/services/telegram_auth.py — that one verifies Telegram WebApp
initData for the Mini Apps; this one is a plain username/password session for a page
opened directly in a browser, outside Telegram entirely.
"""

import hashlib
import hmac
import time

from core.config import settings

SESSION_MAX_AGE_SECONDS = 12 * 60 * 60


def verify_credentials(login: str, password: str) -> bool:
    return hmac.compare_digest(login, settings.admin_web_login) and hmac.compare_digest(
        password, settings.admin_web_password
    )


def _secret_key() -> bytes:
    return hashlib.sha256(f"{settings.admin_web_login}:{settings.admin_web_password}".encode()).digest()


def issue_token() -> str:
    issued_at = str(int(time.time()))
    signature = hmac.new(_secret_key(), issued_at.encode(), hashlib.sha256).hexdigest()
    return f"{issued_at}.{signature}"


def verify_token(token: str) -> bool:
    try:
        issued_at, signature = token.split(".", 1)
    except ValueError:
        return False
    expected = hmac.new(_secret_key(), issued_at.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):
        return False
    return time.time() - int(issued_at) <= SESSION_MAX_AGE_SECONDS
