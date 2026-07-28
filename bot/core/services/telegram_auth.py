import hashlib
import hmac
import json
import time
from urllib.parse import parse_qsl

from core.config import settings

INIT_DATA_MAX_AGE_SECONDS = 24 * 60 * 60


class InvalidInitDataError(Exception):
    pass


def _secret_key(bot_token: str) -> bytes:
    return hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()


def _known_bot_tokens() -> list[str]:
    # The backend serves Mini Apps launched from any of the three bots (client, factory,
    # supplier/seller) — a valid initData signed by any one of them is acceptable here.
    return [settings.bot_token, settings.admin_bot_token, settings.seller_bot_token]


def verify_init_data(init_data: str) -> dict:
    """Verify Telegram WebApp initData per https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
    Returns the parsed user dict on success, raises InvalidInitDataError otherwise.
    """
    pairs = dict(parse_qsl(init_data, strict_parsing=True))
    received_hash = pairs.pop("hash", None)
    if not received_hash:
        raise InvalidInitDataError("missing hash")

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(pairs.items()))
    matches_any_bot = any(
        hmac.compare_digest(
            hmac.new(_secret_key(token), data_check_string.encode(), hashlib.sha256).hexdigest(), received_hash
        )
        for token in _known_bot_tokens()
    )
    if not matches_any_bot:
        raise InvalidInitDataError("hash mismatch")

    auth_date = int(pairs.get("auth_date", 0))
    if time.time() - auth_date > INIT_DATA_MAX_AGE_SECONDS:
        raise InvalidInitDataError("initData expired")

    user_raw = pairs.get("user")
    if not user_raw:
        raise InvalidInitDataError("missing user")

    return json.loads(user_raw)
