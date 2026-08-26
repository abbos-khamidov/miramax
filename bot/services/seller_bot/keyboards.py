from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

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


def supplier_menu(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, "menu_my_stores")), KeyboardButton(text=t(lang, "menu_add_store"))],
            [KeyboardButton(text=t(lang, "menu_analytics")), KeyboardButton(text=t(lang, "menu_language"))],
        ],
        resize_keyboard=True,
    )


def seller_menu(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, "seller_menu_issue_points"))],
            [KeyboardButton(text=t(lang, "menu_add_store")), KeyboardButton(text=t(lang, "seller_menu_add_client"))],
            [KeyboardButton(text=t(lang, "seller_menu_info")), KeyboardButton(text=t(lang, "seller_menu_support"))],
            [KeyboardButton(text=t(lang, "menu_language"))],
        ],
        resize_keyboard=True,
    )


def back_menu(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=t(lang, "submenu_back"))]], resize_keyboard=True)


def match_list_menu(lang: str, labels: list[str], allow_new: bool = False) -> ReplyKeyboardMarkup:
    keyboard = [[KeyboardButton(text=label)] for label in labels]
    if allow_new:
        keyboard.append([KeyboardButton(text=t(lang, "match_create_new"))])
    keyboard.append([KeyboardButton(text=t(lang, "submenu_back"))])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def language_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=label) for label in LANGUAGE_LABELS.values()]],
        resize_keyboard=True,
    )


def confirm_new_client_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=t(lang, "confirm_yes"), callback_data="new_client_yes"),
                InlineKeyboardButton(text=t(lang, "confirm_no"), callback_data="new_client_no"),
            ]
        ]
    )


def tier_composer_keyboard(lang: str, tiers: dict[int, int], cart: dict[int, int]) -> InlineKeyboardMarkup:
    """One coupon-style button per active tier (номинал), showing ×N once tapped,
    plus a confirm/reset row once something is in the cart."""
    rows = []
    for tier, points in tiers.items():
        qty = cart.get(tier, 0)
        label = f"{tier:,}".replace(",", " ") + " сум"
        if qty:
            label += f"  ×{qty}"
        rows.append([InlineKeyboardButton(text=label, callback_data=f"tier:{tier}")])

    if cart:
        total_points = sum(points_for_tier(tiers, tier) * qty for tier, qty in cart.items())
        rows.append([InlineKeyboardButton(text=t(lang, "tier_reset_button"), callback_data="tier_reset")])
        confirm_label = (
            t(lang, "tier_confirm_button", points=f"{total_points:,}".replace(",", " "))
            if total_points > 0
            else t(lang, "tier_not_configured_button")
        )
        # Always rendered (never silently missing) — tapping it while unconfigured still
        # routes through tier_confirm, which shows the "не настроено" alert either way.
        rows.append([InlineKeyboardButton(text=confirm_label, callback_data="tier_confirm")])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def points_for_tier(tiers: dict[int, int], tier: int) -> int:
    return tiers.get(tier, 0)
