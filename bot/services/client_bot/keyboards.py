from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    WebAppInfo,
)

from core.config import settings
from services.client_bot.i18n import LANGUAGE_LABELS, all_variants, t

BALANCE_LABELS = all_variants("menu_balance")
PRIZES_LABELS = all_variants("menu_prizes")
HISTORY_LABELS = all_variants("menu_history")
CALL_STORE_LABELS = all_variants("menu_call_store")
INFO_LABELS = all_variants("menu_info")
LANGUAGE_MENU_LABELS = all_variants("menu_language")


def customer_menu(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            # WebApp button — opens the site in one tap, no bot round-trip. Unlike the
            # personalized "Призы" token-link flow below, this carries no identity, so
            # it always opens (no initData dependency) but shows the generic public
            # catalog rather than the customer's own balance.
            [KeyboardButton(text=t(lang, "menu_bonus_site"), web_app=WebAppInfo(url=settings.miniapp_url))],
            [KeyboardButton(text=t(lang, "menu_prizes"))],
            [KeyboardButton(text=t(lang, "menu_balance")), KeyboardButton(text=t(lang, "menu_history"))],
            [KeyboardButton(text=t(lang, "menu_call_store")), KeyboardButton(text=t(lang, "menu_info"))],
            [KeyboardButton(text=t(lang, "menu_language"))],
        ],
        resize_keyboard=True,
    )


def call_store_keyboard(lang: str, phone: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=t(lang, "call_store_button"), url=f"tel:{phone}")]]
    )


def catalog_link_keyboard(lang: str, url: str) -> InlineKeyboardMarkup:
    """A plain https:// link (not a WebApp button) — the WebApp bridge has proven
    unreliable on some real devices (initData comes back empty), so the Mini App is
    opened as an ordinary link with a signed token embedded (core/services/link_auth.py)."""
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t(lang, "open_catalog_button"), url=url)]])


def language_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=label) for label in LANGUAGE_LABELS.values()]],
        resize_keyboard=True,
    )
