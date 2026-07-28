LANGS = ("ru", "uz", "tr")
DEFAULT_LANG = "ru"

LANGUAGE_LABELS = {
    "ru": "🇷🇺 Русский",
    "uz": "🇺🇿 Oʻzbekcha",
    "tr": "🇹🇷 Türkçe",
}
LANGUAGE_CODE_BY_LABEL = {label: code for code, label in LANGUAGE_LABELS.items()}

CHOOSE_LANGUAGE_FIRST_RUN = "Выберите язык интерфейса:\nTilni tanlang:\nDil seçin:"

# Shown once on first /start, before the language is known — role-specific, all three languages at once.
FIRST_RUN_INSTRUCTION = {
    "supplier": (
        "<b>Miramax Bonus — бот Поставщика</b>\n"
        "Здесь можно добавлять магазины и продавцов, смотреть аналитику по своей сети.\n\n"
        "<b>Miramax Bonus — Yetkazib beruvchi boti</b>\n"
        "Bu yerda do'kon va sotuvchi qo'shishingiz, o'z tarmog'ingiz bo'yicha analitikani ko'rishingiz mumkin.\n\n"
        "<b>Miramax Bonus — Tedarikçi botu</b>\n"
        "Burada mağaza ve satıcı ekleyebilir, kendi ağınızın analizini görebilirsiniz."
    ),
    "seller": (
        "<b>Miramax Bonus — бот Продавца</b>\n"
        "Здесь можно добавлять магазины и клиентов, начислять баллы, подтверждать обмен баллов на товары.\n\n"
        "<b>Miramax Bonus — Sotuvchi boti</b>\n"
        "Bu yerda do'kon va mijoz qo'shishingiz, ball qo'shishingiz, ballarni tovarga almashtirishni tasdiqlashingiz mumkin.\n\n"
        "<b>Miramax Bonus — Satıcı botu</b>\n"
        "Burada mağaza ve müşteri ekleyebilir, puan yükleyebilir, puan-ürün takasını onaylayabilirsiniz."
    ),
}

TRANSLATIONS: dict[str, dict[str, str]] = {
    "ru": {
        "choose_language": "Выберите язык интерфейса:",
        "language_saved": "Готово, дальше буду писать по-русски.",
        "no_access": "Доступ не назначен. Обратитесь к администратору Miramax.",
        "menu_language": "🌐 Язык",
        "help_supplier": (
            "Вы — Поставщик.\n\n"
            "• «➕ Добавить магазин» — вводите имя и фамилию продавца, город и название магазина, "
            "бот сразу выдаёт QR-код. Отправьте его продавцу — по открытии QR он автоматически привяжется "
            "к этому магазину и получит доступ к этому же боту как продавец.\n"
            "• «🏬 Мои магазины» — список ваших магазинов.\n"
            "• «📊 Аналитика по моей сети» — сводка по вашим магазинам."
        ),
        "help_seller": (
            "Вы — Продавец.\n\n"
            "• «➕ Добавить магазин» — открыть ещё одну точку под вашим поставщиком, с QR-кодом для нового продавца.\n"
            "• «➕ Добавить клиента» — вводите телефон, имя и сумму покупки — баллы начисляются сразу.\n"
            "• «🆕 Новинки» — последние товары в каталоге.\n"
            "• «💰 Баллы» — проверить баланс баллов клиента.\n"
            "• «🔄 Обмен» — подтвердить выдачу товара клиенту, который обменял баллы в своём боте.\n"
            "• «ℹ️ Информация» — как работает программа лояльности.\n"
            "• «🆘 Поддержка» — связаться с Miramax."
        ),
        # supplier menu
        "menu_my_stores": "🏬 Мои магазины",
        "menu_add_store": "➕ Добавить магазин",
        "menu_analytics": "📊 Аналитика по моей сети",
        "no_supplier_link": "Ваш аккаунт не привязан к поставщику.",
        "my_stores_empty": "Магазинов пока нет. Добавьте первый через меню «Добавить магазин».",
        "my_stores_header": "Ваши магазины:",
        "my_stores_line": "• {name} — {city}",
        "ask_seller_first_name": "Имя продавца этого магазина?",
        "ask_seller_last_name": "Фамилия?",
        "ask_city": "Город?",
        "ask_store_name": "Название магазина?",
        "store_created": (
            "Магазин «{store_name}» ({city}) добавлен.\n"
            "Продавец: {first_name} {last_name}.\n\n"
            "Отправьте этот QR или ссылку продавцу — открыв её, он сразу привяжется к магазину:\n{link}"
        ),
        "analytics_empty": "Магазинов пока нет — аналитика появится после добавления магазинов.",
        "analytics_header": "«{supplier_name}», магазинов: {store_count}",
        "analytics_line": "• {store_name}: продаж — {total_sales}, начислено баллов — {total_points_issued}",
        # seller menu
        "seller_menu_add_client": "➕ Добавить клиента",
        "seller_menu_novinki": "🆕 Новинки",
        "seller_menu_balance": "💰 Баллы",
        "seller_menu_exchange": "🔄 Обмен",
        "seller_menu_info": "ℹ️ Информация",
        "seller_menu_support": "🆘 Поддержка",
        "no_store_link": "Ваш аккаунт не привязан к магазину.",
        "ask_client_phone": "Номер телефона покупателя?",
        "ask_client_name": "Имя покупателя?",
        "ask_client_amount": "Сумма покупки?",
        "amount_invalid": "Не понял сумму, введите число, например 150000.",
        "client_points_added": "Начислено {points} баллов покупателю «{name}» за покупку на {amount}.",
        "new_customer_invite_caption": (
            "Этот покупатель ещё не открывал бот. Отправьте ему эту ссылку/QR — "
            "открыв её, он сразу увидит свои баллы:\n{link}"
        ),
        "novinki_empty": "Новых товаров пока нет.",
        "novinki_header": "🆕 Последние товары в каталоге:",
        "novinki_line": "• {name} — {category} · {points_cost} баллов",
        "ask_lookup_phone": "Номер телефона или имя покупателя?",
        "lookup_not_found": "Покупатель не найден.",
        "match_list_header": "Найдено несколько совпадений — выберите:",
        "match_list_line": "{name} — {phone}",
        "match_create_new": "➕ Новый клиент",
        "balance_result": "«{name}» ({phone}): баланс — {balance} баллов.",
        "exchange_none_pending": "У этого покупателя нет заявок на обмен баллов.",
        "exchange_list_header": "Заявки на обмен «{name}»:",
        "exchange_item_button": "{product_name} x{qty} — {points} баллов",
        "exchange_confirmed": "Обмен подтверждён: «{product_name}» x{qty}, списано {points} баллов.",
        "exchange_insufficient_balance": "У клиента не хватает баллов на эту заявку: нужно {needed}, доступно {balance}.",
        "exchange_customer_notify": "🎁 Ваш обмен «{product_name}» x{qty} подтверждён и выдан в магазине.",
        "exchange_already_done": "Эта заявка уже обработана.",
        "submenu_back": "⬅️ Назад",
        "info_text": (
            "<b>Как работает программа лояльности Miramax Bonus</b>\n\n"
            "• За каждую покупку клиент получает 5% от суммы баллами.\n"
            "• Баллы копятся на карте клиента и видны ему в боте.\n"
            "• Баллы можно обменять на товары из каталога — заявку клиент оформляет в своём боте, "
            "а выдачу товара подтверждает продавец через «🔄 Обмен»."
        ),
        "support_text": "Вопросы и проблемы — пишите в поддержку Miramax: @miramax_support.",
        "watch_video_prompt": "Чтобы лучше понять, как пользоваться ботом, посмотрите короткое видео 👇",
    },
    "uz": {
        "choose_language": "Interfeys tilini tanlang:",
        "language_saved": "Tayyor, endi o'zbek tilida yozaman.",
        "no_access": "Sizga ruxsat berilmagan. Miramax administratoriga murojaat qiling.",
        "menu_language": "🌐 Til",
        "help_supplier": (
            "Siz — Yetkazib beruvchi.\n\n"
            "• «➕ Do'kon qo'shish» — sotuvchining ismi-familiyasi, shahar va do'kon nomini kiritasiz, "
            "bot darhol QR-kod beradi. Uni sotuvchiga yuboring — QR ochilgach, u avtomatik ravishda "
            "shu do'konga bog'lanadi va shu botda sotuvchi sifatida kirish huquqini oladi.\n"
            "• «🏬 Mening do'konlarim» — do'konlaringiz ro'yxati.\n"
            "• «📊 Tarmog'im bo'yicha analitika» — do'konlaringiz bo'yicha hisobot."
        ),
        "help_seller": (
            "Siz — Sotuvchi.\n\n"
            "• «➕ Do'kon qo'shish» — yetkazib beruvchingiz ostida yana bitta nuqta ochish, yangi sotuvchi uchun QR bilan.\n"
            "• «➕ Mijoz qo'shish» — telefon, ism va xarid summasini kiritasiz — ball darhol qo'shiladi.\n"
            "• «🆕 Yangiliklar» — katalogdagi so'nggi tovarlar.\n"
            "• «💰 Ballar» — mijozning ball balansini tekshirish.\n"
            "• «🔄 Almashtirish» — o'z botida ballarni almashtirgan mijozga tovar berishni tasdiqlash.\n"
            "• «ℹ️ Ma'lumot» — sodiqlik dasturi qanday ishlaydi.\n"
            "• «🆘 Yordam» — Miramax bilan bog'lanish."
        ),
        "menu_my_stores": "🏬 Mening do'konlarim",
        "menu_add_store": "➕ Do'kon qo'shish",
        "menu_analytics": "📊 Tarmog'im bo'yicha analitika",
        "no_supplier_link": "Sizning hisobingiz yetkazib beruvchiga bog'lanmagan.",
        "my_stores_empty": "Hozircha do'kon yo'q. «Do'kon qo'shish» orqali birinchisini qo'shing.",
        "my_stores_header": "Sizning do'konlaringiz:",
        "my_stores_line": "• {name} — {city}",
        "ask_seller_first_name": "Shu do'kon sotuvchisining ismi?",
        "ask_seller_last_name": "Familiyasi?",
        "ask_city": "Shahar?",
        "ask_store_name": "Do'kon nomi?",
        "store_created": (
            "«{store_name}» ({city}) do'koni qo'shildi.\n"
            "Sotuvchi: {first_name} {last_name}.\n\n"
            "Bu QR yoki havolani sotuvchiga yuboring — ochilgach, u darhol shu do'konga bog'lanadi:\n{link}"
        ),
        "analytics_empty": "Hozircha do'kon yo'q — do'kon qo'shilgach analitika paydo bo'ladi.",
        "analytics_header": "«{supplier_name}», do'konlar: {store_count}",
        "analytics_line": "• {store_name}: sotuvlar — {total_sales}, qo'shilgan ball — {total_points_issued}",
        "seller_menu_add_client": "➕ Mijoz qo'shish",
        "seller_menu_novinki": "🆕 Yangiliklar",
        "seller_menu_balance": "💰 Ballar",
        "seller_menu_exchange": "🔄 Almashtirish",
        "seller_menu_info": "ℹ️ Ma'lumot",
        "seller_menu_support": "🆘 Yordam",
        "no_store_link": "Sizning hisobingiz do'konga bog'lanmagan.",
        "ask_client_phone": "Xaridorning telefon raqami?",
        "ask_client_name": "Xaridorning ismi?",
        "ask_client_amount": "Xarid summasi?",
        "amount_invalid": "Summani tushunmadim, raqam kiriting, masalan 150000.",
        "client_points_added": "«{name}» xaridoriga {amount} summadagi xarid uchun {points} ball qo'shildi.",
        "new_customer_invite_caption": (
            "Bu xaridor hali botni ochmagan. Unga shu havola/QR-ni yuboring — "
            "ochgach, u darhol o'z ballarini ko'radi:\n{link}"
        ),
        "novinki_empty": "Hozircha yangi tovar yo'q.",
        "novinki_header": "🆕 Katalogdagi so'nggi tovarlar:",
        "novinki_line": "• {name} — {category} · {points_cost} ball",
        "ask_lookup_phone": "Xaridorning telefon raqami yoki ismi?",
        "lookup_not_found": "Xaridor topilmadi.",
        "match_list_header": "Bir nechta mos keldi — birini tanlang:",
        "match_list_line": "{name} — {phone}",
        "match_create_new": "➕ Yangi xaridor",
        "balance_result": "«{name}» ({phone}): balans — {balance} ball.",
        "exchange_none_pending": "Bu xaridorning almashtirish arizalari yo'q.",
        "exchange_list_header": "«{name}» ning almashtirish arizalari:",
        "exchange_item_button": "{product_name} x{qty} — {points} ball",
        "exchange_confirmed": "Almashtirish tasdiqlandi: «{product_name}» x{qty}, {points} ball yechildi.",
        "exchange_insufficient_balance": "Xaridorda bu ariza uchun ball yetarli emas: kerak {needed}, mavjud {balance}.",
        "exchange_customer_notify": "🎁 Sizning «{product_name}» x{qty} almashtiruvingiz tasdiqlandi va do'konda berildi.",
        "exchange_already_done": "Bu ariza allaqachon ko'rib chiqilgan.",
        "submenu_back": "⬅️ Orqaga",
        "info_text": (
            "<b>Miramax Bonus sodiqlik dasturi qanday ishlaydi</b>\n\n"
            "• Har bir xarid uchun mijoz summaning 5% ini ball sifatida oladi.\n"
            "• Ballar mijoz kartasida to'planadi va uning botida ko'rinadi.\n"
            "• Ballarni katalogdagi tovarlarga almashtirish mumkin — mijoz o'z botida ariza beradi, "
            "tovarni berishni esa sotuvchi «🔄 Almashtirish» orqali tasdiqlaydi."
        ),
        "support_text": "Savol va muammolar bo'yicha Miramax yordamiga yozing: @miramax_support.",
        "watch_video_prompt": "Botdan qanday foydalanishni yaxshiroq tushunish uchun qisqacha videoni tomosha qiling 👇",
    },
    "tr": {
        "choose_language": "Arayüz dilini seçin:",
        "language_saved": "Tamam, bundan sonra Türkçe yazacağım.",
        "no_access": "Erişim tanımlanmamış. Miramax yöneticisiyle iletişime geçin.",
        "menu_language": "🌐 Dil",
        "help_supplier": (
            "Siz — Tedarikçisiniz.\n\n"
            "• «➕ Mağaza ekle» — satıcının ad-soyadını, şehir ve mağaza adını girin, "
            "bot hemen bir QR kod verir. Satıcıya gönderin — QR açıldığında otomatik olarak "
            "bu mağazaya bağlanır ve aynı botta satıcı olarak erişim kazanır.\n"
            "• «🏬 Mağazalarım» — mağazalarınızın listesi.\n"
            "• «📊 Ağımın analizi» — mağazalarınıza göre özet."
        ),
        "help_seller": (
            "Siz — Satıcısınız.\n\n"
            "• «➕ Mağaza ekle» — tedarikçiniz altında yeni bir nokta açın, yeni satıcı için QR ile.\n"
            "• «➕ Müşteri ekle» — telefon, ad ve satış tutarını girin — puan hemen yüklenir.\n"
            "• «🆕 Yenilikler» — katalogdaki son ürünler.\n"
            "• «💰 Puanlar» — bir müşterinin puan bakiyesini kontrol edin.\n"
            "• «🔄 Takas» — kendi botunda puanını ürüne çeviren müşteriye teslimatı onaylayın.\n"
            "• «ℹ️ Bilgi» — sadakat programı nasıl işler.\n"
            "• «🆘 Destek» — Miramax ile iletişime geçin."
        ),
        "menu_my_stores": "🏬 Mağazalarım",
        "menu_add_store": "➕ Mağaza ekle",
        "menu_analytics": "📊 Ağımın analizi",
        "no_supplier_link": "Hesabınız bir tedarikçiye bağlı değil.",
        "my_stores_empty": "Henüz mağaza yok. «Mağaza ekle» ile ilkini ekleyin.",
        "my_stores_header": "Mağazalarınız:",
        "my_stores_line": "• {name} — {city}",
        "ask_seller_first_name": "Bu mağazanın satıcısının adı?",
        "ask_seller_last_name": "Soyadı?",
        "ask_city": "Şehir?",
        "ask_store_name": "Mağaza adı?",
        "store_created": (
            "«{store_name}» ({city}) mağazası eklendi.\n"
            "Satıcı: {first_name} {last_name}.\n\n"
            "Bu QR'ı veya bağlantıyı satıcıya gönderin — açıldığında hemen bu mağazaya bağlanır:\n{link}"
        ),
        "analytics_empty": "Henüz mağaza yok — mağaza eklendikten sonra analiz görünecek.",
        "analytics_header": "«{supplier_name}», mağazalar: {store_count}",
        "analytics_line": "• {store_name}: satışlar — {total_sales}, yüklenen puan — {total_points_issued}",
        "seller_menu_add_client": "➕ Müşteri ekle",
        "seller_menu_novinki": "🆕 Yenilikler",
        "seller_menu_balance": "💰 Puanlar",
        "seller_menu_exchange": "🔄 Takas",
        "seller_menu_info": "ℹ️ Bilgi",
        "seller_menu_support": "🆘 Destek",
        "no_store_link": "Hesabınız bir mağazaya bağlı değil.",
        "ask_client_phone": "Müşterinin telefon numarası?",
        "ask_client_name": "Müşterinin adı?",
        "ask_client_amount": "Satış tutarı?",
        "amount_invalid": "Tutarı anlamadım, bir sayı girin, örneğin 150000.",
        "client_points_added": "«{name}» müşterisine {amount} tutarındaki satış için {points} puan yüklendi.",
        "new_customer_invite_caption": (
            "Bu müşteri botu henüz açmadı. Bu bağlantıyı/QR'ı gönderin — "
            "açtığında puanlarını hemen görür:\n{link}"
        ),
        "novinki_empty": "Henüz yeni ürün yok.",
        "novinki_header": "🆕 Katalogdaki son ürünler:",
        "novinki_line": "• {name} — {category} · {points_cost} puan",
        "ask_lookup_phone": "Müşterinin telefon numarası veya adı?",
        "lookup_not_found": "Müşteri bulunamadı.",
        "match_list_header": "Birden fazla eşleşme bulundu — birini seçin:",
        "match_list_line": "{name} — {phone}",
        "match_create_new": "➕ Yeni müşteri",
        "balance_result": "«{name}» ({phone}): bakiye — {balance} puan.",
        "exchange_none_pending": "Bu müşterinin bekleyen takas talebi yok.",
        "exchange_list_header": "«{name}» için takas talepleri:",
        "exchange_item_button": "{product_name} x{qty} — {points} puan",
        "exchange_confirmed": "Takas onaylandı: «{product_name}» x{qty}, {points} puan düşüldü.",
        "exchange_insufficient_balance": "Müşterinin bu talep için puanı yetersiz: gereken {needed}, mevcut {balance}.",
        "exchange_customer_notify": "🎁 «{product_name}» x{qty} takasınız onaylandı ve mağazada teslim edildi.",
        "exchange_already_done": "Bu talep zaten işlendi.",
        "submenu_back": "⬅️ Geri",
        "info_text": (
            "<b>Miramax Bonus sadakat programı nasıl işler</b>\n\n"
            "• Her satıştan müşteri tutarın %5'ini puan olarak kazanır.\n"
            "• Puanlar müşteri kartında birikir ve kendi botunda görünür.\n"
            "• Puanlar katalogdaki ürünlerle takas edilebilir — müşteri talebi kendi botunda oluşturur, "
            "teslimatı ise satıcı «🔄 Takas» üzerinden onaylar."
        ),
        "support_text": "Sorular ve sorunlar için Miramax destek ile iletişime geçin: @miramax_support.",
        "watch_video_prompt": "Botu nasıl kullanacağınızı daha iyi anlamak için kısa videoyu izleyin 👇",
    },
}


def t(lang: str | None, key: str, **kwargs) -> str:
    lang = lang if lang in TRANSLATIONS else DEFAULT_LANG
    text = TRANSLATIONS[lang][key]
    return text.format(**kwargs) if kwargs else text


def all_variants(key: str) -> set[str]:
    return {TRANSLATIONS[lang][key] for lang in LANGS}
