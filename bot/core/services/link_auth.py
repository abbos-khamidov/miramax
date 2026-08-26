"""Fallback auth for the Mini App when opened as a plain link instead of through
Telegram's WebApp bridge (KeyboardButton.web_app has proven unreliable on some real
devices — initData comes back empty). The bot embeds one of these signed tokens in
the link it sends the customer; the token carries nothing but the telegram_id, so a
plain https:// link works from any browser without depending on the WebApp bridge.
"""
import hashlib
import hmac

from core.config import settings


class InvalidLinkTokenError(Exception):
    pass


def issue_link_token(telegram_id: int) -> str:
    payload = str(telegram_id)
    signature = hmac.new(settings.bot_token.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{signature}"


def verify_link_token(token: str) -> int:
    payload, _, signature = token.partition(".")
    if not payload or not signature:
        raise InvalidLinkTokenError("malformed token")
    expected = hmac.new(settings.bot_token.encode(), payload.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):
        raise InvalidLinkTokenError("signature mismatch")
    try:
        return int(payload)
    except ValueError:
        raise InvalidLinkTokenError("bad payload") from None
