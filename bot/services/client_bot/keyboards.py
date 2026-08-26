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
NEW_LABELS = all_variants("menu_new")
PRIZES_LABELS = all_variants("menu_prizes")
HISTORY_LABELS = all_variants("menu_history")
CALL_STORE_LABELS = all_variants("menu_call_store")
INFO_LABELS = all_variants("menu_info")
LANGUAGE_MENU_LABELS = all_variants("menu_language")


def customer_menu(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=t(lang, "menu_new"), web_app=WebAppInfo(url=f"{settings.miniapp_url}?tab=new")),
                KeyboardButton(text=t(lang, "menu_prizes"), web_app=WebAppInfo(url=f"{settings.miniapp_url}?tab=catalog")),
            ],
            [KeyboardButton(text=t(lang, "menu_balance")), KeyboardButton(text=t(lang, "menu_history"))],
            [KeyboardButton(text=t(lang, "menu_call_store")), KeyboardButton(text=t(lang, "menu_info"))],
            [KeyboardButton(text=t(lang, "menu_language"))],
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
