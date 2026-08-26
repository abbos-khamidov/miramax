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
        "menu_open_catalog": "🛍 Открыть каталог",
        "menu_balance": "💎 Мои баллы",
        "menu_products": "📦 Товары",
        "menu_search": "🔎 Поиск товара",
        "menu_history": "🧾 История обменов",
        "menu_redeem": "🎁 Обменять баллы",
        "menu_call_store": "📞 Позвонить в магазин",
        "menu_language": "🌐 Язык",
        "call_store_text": "Звоните нам: {phone}",
        "call_store_button": "📞 Позвонить",
        "start_greeting": "Кабинет клиента Miramax Bonus. Смотрите баллы, ищите товары или откройте каталог.",
        "welcome_after_invite": "🎉 Добро пожаловать в Miramax Bonus! Ваш баланс: <b>{balance} баллов</b>.",
        "balance_label": "Ваш баланс: <b>{balance} баллов</b>.",
        "product_redeem_button": "🎁 Обменять на баллы",
        "redeem_insufficient": "Недостаточно баллов для этого обмена: нужно {cost}, у вас {balance}.",
        "redeem_product_not_found": "Товар не найден или недоступен.",
        "redeem_created": (
            "Заявка на обмен создана: <b>{name}</b> x{qty} — {points} баллов.\n"
            "Покажите этот экран продавцу в магазине, чтобы получить товар."
        ),
        "menu_info": "ℹ️ Информация",
        "info_text": (
            "<b>Как работает Miramax Bonus</b>\n\n"
            "• За каждую покупку в магазине вам начисляют баллы — 5% от суммы покупки.\n"
            "• Баллы сразу видны в разделе «💎 Мои баллы».\n"
            "• «📦 Товары» — что можно получить за баллы.\n"
            "• «🎁 Обменять баллы» — выберите товар и нажмите «Обменять на баллы», заявка уйдёт продавцу.\n"
            "• Заберите товар в магазине — продавец подтвердит обмен, и баллы спишутся.\n"
            "• «🧾 История обменов» — все ваши покупки и обмены."
        ),
    },
    "uz": {
        "choose_language": "Interfeys tilini tanlang:",
        "language_saved": "Tayyor, endi o'zbek tilida yozaman.",
        "menu_open_catalog": "🛍 Katalogni ochish",
        "menu_balance": "💎 Ballarim",
        "menu_products": "📦 Tovarlar",
        "menu_search": "🔎 Tovar qidirish",
        "menu_history": "🧾 Almashtirish tarixi",
        "menu_redeem": "🎁 Ballarni almashtirish",
        "menu_call_store": "📞 Do'konga qo'ng'iroq",
        "menu_language": "🌐 Til",
        "call_store_text": "Bizga qo'ng'iroq qiling: {phone}",
        "call_store_button": "📞 Qo'ng'iroq qilish",
        "start_greeting": "Miramax Bonus mijoz kabineti. Ballaringizni ko'ring, tovar qidiring yoki katalogni oching.",
        "welcome_after_invite": "🎉 Miramax Bonus'ga xush kelibsiz! Balansingiz: <b>{balance} ball</b>.",
        "balance_label": "Sizning balansingiz: <b>{balance} ball</b>.",
        "product_redeem_button": "🎁 Ballarga almashtirish",
        "redeem_insufficient": "Bu almashtirish uchun ball yetarli emas: kerak {cost}, sizda {balance}.",
        "redeem_product_not_found": "Tovar topilmadi yoki faol emas.",
        "redeem_created": (
            "Almashtirish arizasi yaratildi: <b>{name}</b> x{qty} — {points} ball.\n"
            "Tovarni olish uchun sotuvchiga shu ekranni ko'rsating."
        ),
        "menu_info": "ℹ️ Ma'lumot",
        "info_text": (
            "<b>Miramax Bonus qanday ishlaydi</b>\n\n"
            "• Magazindagi har bir xarid uchun ball beriladi — xarid summasining 5%.\n"
            "• Ballar darhol «💎 Ballarim» bo'limida ko'rinadi.\n"
            "• «📦 Tovarlar» — ballarga nima olish mumkinligini ko'rsatadi.\n"
            "• «🎁 Ballarni almashtirish» — tovarni tanlab «Ballarga almashtirish»ni bosing, ariza sotuvchiga boradi.\n"
            "• Tovarni do'kondan oling — sotuvchi almashtirishni tasdiqlaydi va ballar yechiladi.\n"
            "• «🧾 Almashtirish tarixi» — barcha xarid va almashtiruvlaringiz."
        ),
    },
    "tr": {
        "choose_language": "Arayüz dilini seçin:",
        "language_saved": "Tamam, bundan sonra Türkçe yazacağım.",
        "menu_open_catalog": "🛍 Kataloğu aç",
        "menu_balance": "💎 Puanlarım",
        "menu_products": "📦 Ürünler",
        "menu_search": "🔎 Ürün ara",
        "menu_history": "🧾 Takas geçmişi",
        "menu_redeem": "🎁 Puanları takas et",
        "menu_call_store": "📞 Mağazayı ara",
        "menu_language": "🌐 Dil",
        "call_store_text": "Bizi arayın: {phone}",
        "call_store_button": "📞 Ara",
        "start_greeting": "Miramax Bonus müşteri paneli. Puanlarınıza bakın, ürün arayın veya kataloğu açın.",
        "welcome_after_invite": "🎉 Miramax Bonus'a hoş geldiniz! Bakiyeniz: <b>{balance} puan</b>.",
        "balance_label": "Bakiyeniz: <b>{balance} puan</b>.",
        "product_redeem_button": "🎁 Puanla takas et",
        "redeem_insufficient": "Bu takas için puan yetersiz: gereken {cost}, sizde {balance}.",
        "redeem_product_not_found": "Ürün bulunamadı veya aktif değil.",
        "redeem_created": (
            "Takas talebi oluşturuldu: <b>{name}</b> x{qty} — {points} puan.\n"
            "Ürünü almak için bu ekranı satıcıya gösterin."
        ),
        "menu_info": "ℹ️ Bilgi",
        "info_text": (
            "<b>Miramax Bonus nasıl çalışır</b>\n\n"
            "• Mağazadaki her satıştan puan kazanırsınız — tutarın %5'i.\n"
            "• Puanlar hemen «💎 Puanlarım» bölümünde görünür.\n"
            "• «📦 Ürünler» — puanla neler alabileceğinizi gösterir.\n"
            "• «🎁 Puanları takas et» — bir ürün seçip «Puanla takas et»e basın, talep satıcıya gider.\n"
            "• Ürünü mağazadan alın — satıcı takası onaylar ve puanlar düşülür.\n"
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
