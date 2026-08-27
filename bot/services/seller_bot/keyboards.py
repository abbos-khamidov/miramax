from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    WebAppInfo,
)

from core.config import settings
from services.seller_bot.i18n import LANGUAGE_LABELS, all_variants, t

MY_STORES_LABELS = all_variants("menu_my_stores")
ADD_STORE_LABELS = all_variants("menu_add_store")
ANALYTICS_LABELS = all_variants("menu_analytics")
LANGUAGE_MENU_LABELS = all_variants("menu_language")

ISSUE_POINTS_LABELS = all_variants("seller_menu_issue_points")
ADD_CLIENT_LABELS = all_variants("seller_menu_add_client")
INFO_LABELS = all_variants("seller_menu_info")
SUPPORT_LABELS = all_variants("seller_menu_support")
BACK_LABELS = all_variants("submenu_back")
CANCEL_LABELS = all_variants("cancel_action")
BACK_OR_CANCEL_LABELS = BACK_LABELS | CANCEL_LABELS


def _bonus_site_button(lang: str) -> KeyboardButton:
    # WebApp button, one tap, same mechanism as admin_bot's "Открыть аналитику".
    return KeyboardButton(text=t(lang, "menu_bonus_site"), web_app=WebAppInfo(url=settings.miniapp_url))


def supplier_menu(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [_bonus_site_button(lang)],
            [KeyboardButton(text=t(lang, "menu_my_stores")), KeyboardButton(text=t(lang, "menu_add_store"))],
            [KeyboardButton(text=t(lang, "menu_analytics")), KeyboardButton(text=t(lang, "menu_language"))],
        ],
        resize_keyboard=True,
    )


def seller_menu(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [_bonus_site_button(lang)],
            [KeyboardButton(text=t(lang, "seller_menu_issue_points"))],
            [KeyboardButton(text=t(lang, "menu_add_store")), KeyboardButton(text=t(lang, "seller_menu_add_client"))],
            [KeyboardButton(text=t(lang, "seller_menu_info")), KeyboardButton(text=t(lang, "seller_menu_support"))],
            [KeyboardButton(text=t(lang, "menu_language"))],
        ],
        resize_keyboard=True,
    )


def back_menu(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t(lang, "submenu_back")), KeyboardButton(text=t(lang, "cancel_action"))]],
        resize_keyboard=True,
    )


def match_list_menu(lang: str, labels: list[str], allow_new: bool = False) -> ReplyKeyboardMarkup:
    keyboard = [[KeyboardButton(text=label)] for label in labels]
    if allow_new:
        keyboard.append([KeyboardButton(text=t(lang, "match_create_new"))])
    keyboard.append([KeyboardButton(text=t(lang, "submenu_back")), KeyboardButton(text=t(lang, "cancel_action"))])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def language_menu(cancel_lang: str | None = None) -> ReplyKeyboardMarkup:
    """cancel_lang adds a Cancel row — only when there's somewhere to cancel back to
    (an existing role.language). First-run language pick has none, it's mandatory."""
    keyboard = [[KeyboardButton(text=label) for label in LANGUAGE_LABELS.values()]]
    if cancel_lang is not None:
        keyboard.append([KeyboardButton(text=t(cancel_lang, "cancel_action"))])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def confirm_new_client_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t(lang, "confirm_yes"), callback_data="new_client_yes"),
                InlineKeyboardButton(text=t(lang, "confirm_no"), callback_data="new_client_no"),
            ]
        ]
    )


def tier_composer_keyboard(lang: str, tier_amounts: list[int], cart: dict[int, int], total_points: int) -> InlineKeyboardMarkup:
    """One coupon-style button per active номинал amount, showing ×N once tapped,
    plus a confirm/reset row once something is in the cart. total_points is computed
    by the caller off the whole cart's sum (core/services/tiers.py:points_for_cart) —
    a single global rate, not a per-tier value baked into this keyboard."""
    rows = []
    for tier in tier_amounts:
        qty = cart.get(tier, 0)
        label = f"{tier:,}".replace(",", " ") + " сум"
        if qty:
            label += f"  ×{qty}"
        rows.append([InlineKeyboardButton(text=label, callback_data=f"tier:{tier}")])

    if cart:
        rows.append([InlineKeyboardButton(text=t(lang, "tier_reset_button"), callback_data="tier_reset")])
        confirm_label = (
            t(lang, "tier_confirm_button", points=f"{total_points:,}".replace(",", " "))
            if total_points > 0
            else t(lang, "tier_amount_too_small_button")
        )
        # Always rendered (never silently missing) — tapping it while the sum is still
        # too small for even 1 point still routes through tier_confirm, which shows an alert.
        rows.append([InlineKeyboardButton(text=confirm_label, callback_data="tier_confirm")])

    return InlineKeyboardMarkup(inline_keyboard=rows)
