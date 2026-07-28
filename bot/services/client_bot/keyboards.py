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
PRODUCTS_LABELS = all_variants("menu_products")
SEARCH_LABELS = all_variants("menu_search")
HISTORY_LABELS = all_variants("menu_history")
REDEEM_LABELS = all_variants("menu_redeem")
CALL_STORE_LABELS = all_variants("menu_call_store")
INFO_LABELS = all_variants("menu_info")
LANGUAGE_MENU_LABELS = all_variants("menu_language")


def customer_menu(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, "menu_open_catalog"), web_app=WebAppInfo(url=settings.miniapp_url))],
            [KeyboardButton(text=t(lang, "menu_balance")), KeyboardButton(text=t(lang, "menu_products"))],
            [KeyboardButton(text=t(lang, "menu_search")), KeyboardButton(text=t(lang, "menu_history"))],
            [KeyboardButton(text=t(lang, "menu_redeem")), KeyboardButton(text=t(lang, "menu_call_store"))],
            [KeyboardButton(text=t(lang, "menu_info")), KeyboardButton(text=t(lang, "menu_language"))],
        ],
        resize_keyboard=True,
    )


def call_store_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "call_store_button"), url=f"tel:{settings.store_phone}")]
        ]
    )


def language_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=label) for label in LANGUAGE_LABELS.values()]],
        resize_keyboard=True,
    )


def catalog_webapp_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Katalogni ochish", web_app=WebAppInfo(url=settings.miniapp_url))]
        ]
    )
