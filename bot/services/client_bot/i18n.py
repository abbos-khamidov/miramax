LANGS = ("ru", "uz", "tr")
DEFAULT_LANG = "uz"

LANGUAGE_LABELS = {
    "ru": "🇷🇺 Русский",
    "uz": "🇺🇿 Oʻzbekcha",
    "tr": "🇹🇷 Türkçe",
}
LANGUAGE_CODE_BY_LABEL = {label: code for code, label in LANGUAGE_LABELS.items()}

CHOOSE_LANGUAGE_FIRST_RUN = "Выберите язык интерфейса:\nTilni tanlang:\nDil seçin:"

# Shown before a user even presses Start (empty-chat description + profile short
# description), per Telegram client language_code — see client_bot/bot.py:_set_profile_texts.
PROFILE_DESCRIPTIONS: dict[str | None, str] = {
    None: (
        "Miramax Bonus — do'kon sodiqlik dasturi. Xaridlar uchun ball to'plang va "
        "ularni tovarlarga almashtiring.\n\nBoshlash uchun /start ni bosing."
    ),
    "ru": (
        "Miramax Bonus — бонусная программа магазина. Копите баллы за покупки и "
        "обменивайте их на товары.\n\nНажмите /start, чтобы начать."
    ),
    "tr": (
        "Miramax Bonus — mağaza sadakat programı. Alışverişlerden puan biriktirin ve "
        "ürünlerle takas edin.\n\nBaşlamak için /start yazın."
    ),
}

PROFILE_SHORT_DESCRIPTIONS: dict[str | None, str] = {
    None: "Miramax Bonus — xaridlar uchun ball. Boshlash uchun /start ni bosing.",
    "ru": "Miramax Bonus — баллы за покупки. Нажмите /start, чтобы начать.",
    "tr": "Miramax Bonus — alışverişlerden puan. Başlamak için /start yazın.",
    "en": "Miramax Bonus loyalty program. Send /start to begin.",
}

TRANSLATIONS: dict[str, dict[str, str]] = {
    "ru": {
        "choose_language": "Выберите язык интерфейса:",
        "language_saved": "Готово, дальше буду писать по-русски.",
        "menu_balance": "💎 Мои баллы",
        "menu_new": "🆕 Новинки",
        "menu_prizes": "🎁 Призы",
        "menu_history": "🧾 История обменов",
        "menu_call_store": "📞 Позвонить в магазин",
        "menu_language": "🌐 Язык",
        "call_store_text": "Звоните нам: {phone}",
        "call_store_button": "📞 Позвонить",
        "start_greeting": "Кабинет клиента Miramax Bonus. Смотрите баллы и призы, которые можно получить.",
        "welcome_after_invite": "🎉 Добро пожаловать в Miramax Bonus! Ваш баланс: <b>{balance} баллов</b>.",
        "balance_label": "Ваш баланс: <b>{balance} баллов</b>.",
        "balance_redeem_instructions": "Подойдите в ближайший магазин, где продают продукцию MiramaxMPP, и обменяйте баллы на приз.",
        "balance_current_prize": "✅ Сейчас вам доступно: «{name}» ({points} баллов).",
        "balance_next_prize": "🔜 До приза «{name}» ({points} баллов) не хватает: {needed} баллов.",
        "balance_max_prize": "🏆 У вас достаточно баллов на самый большой приз!",
        "menu_info": "ℹ️ Информация",
        "info_text": (
            "<b>Как работает Miramax Bonus</b>\n\n"
            "• За каждую покупку в магазине вам начисляют баллы.\n"
            "• Баллы сразу видны в разделе «💎 Мои баллы» — там же написано, на какой приз вам уже хватает "
            "и сколько нужно до следующего.\n"
            "• «🎁 Призы» — полный каталог призов и сколько баллов за каждый нужно.\n"
            "• «🆕 Новинки» — последние добавленные призы.\n"
            "• Чтобы получить приз — подойдите в ближайший магазин, где продают продукцию MiramaxMPP, и "
            "обменяйте баллы на месте.\n"
            "• «🧾 История обменов» — все ваши покупки и обмены."
        ),
    },
    "uz": {
        "choose_language": "Interfeys tilini tanlang:",
        "language_saved": "Tayyor, endi o'zbek tilida yozaman.",
        "menu_balance": "💎 Ballarim",
        "menu_new": "🆕 Yangiliklar",
        "menu_prizes": "🎁 Sovg'alar",
        "menu_history": "🧾 Almashtirish tarixi",
        "menu_call_store": "📞 Do'konga qo'ng'iroq",
        "menu_language": "🌐 Til",
        "call_store_text": "Bizga qo'ng'iroq qiling: {phone}",
        "call_store_button": "📞 Qo'ng'iroq qilish",
        "start_greeting": "Miramax Bonus mijoz kabineti. Ballaringizni va qanday sovg'alar borligini ko'ring.",
        "welcome_after_invite": "🎉 Miramax Bonus'ga xush kelibsiz! Balansingiz: <b>{balance} ball</b>.",
        "balance_label": "Sizning balansingiz: <b>{balance} ball</b>.",
        "balance_redeem_instructions": "MiramaxMPP mahsulotlari sotiladigan eng yaqin do'konga boring va ballaringizni sovg'aga almashtiring.",
        "balance_current_prize": "✅ Hozir sizga mavjud: «{name}» ({points} ball).",
        "balance_next_prize": "🔜 «{name}» sovg'asigacha ({points} ball) yetishmayapti: {needed} ball.",
        "balance_max_prize": "🏆 Sizda eng katta sovg'a uchun yetarli ball bor!",
        "menu_info": "ℹ️ Ma'lumot",
        "info_text": (
            "<b>Miramax Bonus qanday ishlaydi</b>\n\n"
            "• Magazindagi har bir xarid uchun ball beriladi.\n"
            "• Ballar darhol «💎 Ballarim» bo'limida ko'rinadi — u yerda qaysi sovg'aga hozir yetarli va "
            "keyingisigacha qancha kerakligi ham yozilgan.\n"
            "• «🎁 Sovg'alar» — barcha sovg'alar va har biriga necha ball kerakligi.\n"
            "• «🆕 Yangiliklar» — so'nggi qo'shilgan sovg'alar.\n"
            "• Sovg'ani olish uchun — MiramaxMPP mahsulotlari sotiladigan eng yaqin do'konga boring va "
            "ballaringizni shu yerda almashtiring.\n"
            "• «🧾 Almashtirish tarixi» — barcha xarid va almashtiruvlaringiz."
        ),
    },
    "tr": {
        "choose_language": "Arayüz dilini seçin:",
        "language_saved": "Tamam, bundan sonra Türkçe yazacağım.",
        "menu_balance": "💎 Puanlarım",
        "menu_new": "🆕 Yenilikler",
        "menu_prizes": "🎁 Ödüller",
        "menu_history": "🧾 Takas geçmişi",
        "menu_call_store": "📞 Mağazayı ara",
        "menu_language": "🌐 Dil",
        "call_store_text": "Bizi arayın: {phone}",
        "call_store_button": "📞 Ara",
        "start_greeting": "Miramax Bonus müşteri paneli. Puanlarınıza ve ödüllere bakın.",
        "welcome_after_invite": "🎉 Miramax Bonus'a hoş geldiniz! Bakiyeniz: <b>{balance} puan</b>.",
        "balance_label": "Bakiyeniz: <b>{balance} puan</b>.",
        "balance_redeem_instructions": "MiramaxMPP ürünlerinin satıldığı en yakın mağazaya gidin ve puanlarınızı bir ödülle takas edin.",
        "balance_current_prize": "✅ Şu anda alabileceğiniz: «{name}» ({points} puan).",
        "balance_next_prize": "🔜 «{name}» ödülüne ({points} puan) kadar eksik: {needed} puan.",
        "balance_max_prize": "🏆 En büyük ödül için yeterli puanınız var!",
        "menu_info": "ℹ️ Bilgi",
        "info_text": (
            "<b>Miramax Bonus nasıl çalışır</b>\n\n"
            "• Mağazadaki her satıştan puan kazanırsınız.\n"
            "• Puanlar hemen «💎 Puanlarım» bölümünde görünür — hangi ödüle şu an yeterli olduğunuz ve "
            "bir sonrakine ne kadar kaldığı da orada yazar.\n"
            "• «🎁 Ödüller» — tüm ödüller ve her biri için gereken puan.\n"
            "• «🆕 Yenilikler» — son eklenen ödüller.\n"
            "• Ödülü almak için — MiramaxMPP ürünlerinin satıldığı en yakın mağazaya gidin ve puanlarınızı "
            "orada takas edin.\n"
            "• «🧾 Takas geçmişi» — tüm satın alma ve takaslarınız."
        ),
    },
}


def t(lang: str | None, key: str, **kwargs) -> str:
    lang = lang if lang in TRANSLATIONS else DEFAULT_LANG
    text = TRANSLATIONS[lang][key]
    return text.format(**kwargs) if kwargs else text


def all_variants(key: str) -> set[str]:
    return {TRANSLATIONS[lang][key] for lang in LANGS}
