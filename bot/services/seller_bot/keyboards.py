from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from services.seller_bot.i18n import LANGUAGE_LABELS, all_variants, t

MY_STORES_LABELS = all_variants("menu_my_stores")
ADD_STORE_LABELS = all_variants("menu_add_store")
ANALYTICS_LABELS = all_variants("menu_analytics")
LANGUAGE_MENU_LABELS = all_variants("menu_language")

ADD_CLIENT_LABELS = all_variants("seller_menu_add_client")
NOVINKI_LABELS = all_variants("seller_menu_novinki")
BALANCE_LABELS = all_variants("seller_menu_balance")
EXCHANGE_LABELS = all_variants("seller_menu_exchange")
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
            [KeyboardButton(text=t(lang, "menu_add_store")), KeyboardButton(text=t(lang, "seller_menu_add_client"))],
            [KeyboardButton(text=t(lang, "seller_menu_novinki")), KeyboardButton(text=t(lang, "seller_menu_balance"))],
            [KeyboardButton(text=t(lang, "seller_menu_exchange")), KeyboardButton(text=t(lang, "seller_menu_info"))],
            [KeyboardButton(text=t(lang, "seller_menu_support")), KeyboardButton(text=t(lang, "menu_language"))],
        ],
        resize_keyboard=True,
    )


def back_menu(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=t(lang, "submenu_back"))]], resize_keyboard=True)


def exchange_list_menu(lang: str, labels: list[str]) -> ReplyKeyboardMarkup:
    keyboard = [[KeyboardButton(text=label)] for label in labels]
    keyboard.append([KeyboardButton(text=t(lang, "submenu_back"))])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


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
