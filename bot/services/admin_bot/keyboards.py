from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from services.admin_bot.i18n import LANGUAGE_LABELS, all_variants, t

ADD_USER_LABELS = all_variants("menu_add_user")
VIEW_USERS_LABELS = all_variants("menu_view_users")
ANALYTICS_LABELS = all_variants("menu_analytics")
POINTS_RATE_LABELS = all_variants("menu_points_rate")
ONLINE_SHOWCASE_LABELS = all_variants("menu_online_showcase")
LANGUAGE_MENU_LABELS = all_variants("menu_language")
ADMIN_LABELS = all_variants("submenu_admin")
WHOLESALER_LABELS = all_variants("submenu_wholesaler")
BACK_LABELS = all_variants("submenu_back")
VIEW_ADMIN_LABELS = all_variants("view_admins")
VIEW_SUPPLIER_LABELS = all_variants("view_suppliers")
VIEW_WHOLESALER_LABELS = all_variants("view_wholesalers")
VIEW_SEARCH_LABELS = all_variants("view_search")


def factory_menu(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, "menu_add_user"))],
            [KeyboardButton(text=t(lang, "menu_view_users"))],
            [KeyboardButton(text=t(lang, "menu_points_rate")), KeyboardButton(text=t(lang, "menu_online_showcase"))],
            [KeyboardButton(text=t(lang, "menu_analytics")), KeyboardButton(text=t(lang, "menu_language"))],
        ],
        resize_keyboard=True,
    )


def add_user_menu(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, "submenu_admin"))],
            [KeyboardButton(text=t(lang, "submenu_wholesaler"))],
            [KeyboardButton(text=t(lang, "submenu_back"))],
        ],
        resize_keyboard=True,
    )


def view_users_menu(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, "view_admins"))],
            [KeyboardButton(text=t(lang, "view_suppliers"))],
            [KeyboardButton(text=t(lang, "view_wholesalers"))],
            [KeyboardButton(text=t(lang, "submenu_back"))],
        ],
        resize_keyboard=True,
    )


def entity_list_menu(lang: str, labels: list[str]) -> ReplyKeyboardMarkup:
    keyboard = [[KeyboardButton(text=label)] for label in labels]
    keyboard.append([KeyboardButton(text=t(lang, "view_search"))])
    keyboard.append([KeyboardButton(text=t(lang, "submenu_back"))])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def language_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=label) for label in LANGUAGE_LABELS.values()]],
        resize_keyboard=True,
    )
