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
        "Здесь можно выдавать баллы покупателям и добавлять магазины/клиентов.\n\n"
        "<b>Miramax Bonus — Sotuvchi boti</b>\n"
        "Bu yerda xaridorlarga ball berish, do'kon/mijoz qo'shish mumkin.\n\n"
        "<b>Miramax Bonus — Satıcı botu</b>\n"
        "Burada müşterilere puan verebilir, mağaza/müşteri ekleyebilirsiniz."
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
        "help_seller": "Вы — Продавец. Полная инструкция — в кнопке «ℹ️ Информация».",
        # supplier menu
        "menu_bonus_site": "🎁 Бонус",
        "bonus_site_text": "Miramax Bonus: {link}",
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
        "ask_store_phone": "Телефон магазина (для кнопки «Позвонить в магазин» у клиентов)?",
        "store_created": (
            "Магазин «{store_name}» ({city}) добавлен.\n"
            "Продавец: {first_name} {last_name}.\n\n"
            "Отправьте этот QR или ссылку продавцу — открыв её, он сразу привяжется к магазину:\n{link}"
        ),
        "analytics_empty": "Магазинов пока нет — аналитика появится после добавления магазинов.",
        "analytics_header": "«{supplier_name}», магазинов: {store_count}",
        "analytics_line": "• {store_name}: продаж — {total_sales}, начислено баллов — {total_points_issued}",
        # seller menu
        "seller_menu_issue_points": "💳 Выдать баллы",
        "seller_menu_add_client": "➕ Добавить клиента",
        "seller_menu_info": "ℹ️ Информация",
        "seller_menu_support": "🆘 Поддержка",
        "no_store_link": "Ваш аккаунт не привязан к магазину.",
        "ask_client_first_name": "Имя покупателя?",
        "ask_client_last_name": "Фамилия покупателя?",
        "ask_client_phone": "Номер телефона покупателя?",
        "new_customer_invite_caption": (
            "Этот покупатель ещё не открывал бот. Отправьте ему эту ссылку/QR — "
            "открыв её, он сразу увидит свои баллы:\n{link}"
        ),
        "match_list_header": "Найдено несколько совпадений — выберите:",
        "match_list_line": "{name} — {phone}",
        "match_create_new": "➕ Новый клиент",
        "client_registered": "Клиент «{name}» зарегистрирован.",
        "client_not_found_confirm": "⚠️ Клиент с таким номером не найден. Добавить нового клиента?",
        "confirm_yes": "✅ Да",
        "confirm_no": "❌ Нет",
        "tier_compose_header": "Выберите сумму покупки (можно нажимать несколько раз):",
        "tier_compose_line": "{tier} сум × {qty}",
        "tier_compose_total": "Сумма покупки: {amount} сум",
        "tier_reset_button": "🔄 Сбросить",
        "tier_confirm_button": "✅ Начислить {points} баллов",
        "tier_not_configured": "Баллы для этой суммы ещё не настроены. Обратитесь к администратору.",
        "tier_not_configured_button": "⚠️ Баллы не настроены",
        "tier_sale_confirmed": "Начислено {points} баллов покупателю «{name}».",
        "submenu_back": "⬅️ Назад",
        "cancel_action": "❌ Отменить действие",
        "info_text": (
            "<b>Как пользоваться ботом Miramax Bonus</b>\n\n"
            "<b>💳 Выдать баллы</b> — главное действие. Вводите имя, фамилию и телефон покупателя. "
            "Если такой покупатель уже есть в базе — бот найдёт его сам (или предложит выбрать, если совпадений "
            "несколько). Дальше нажимайте на карточки с суммами покупки — по одной за каждую сумму, можно "
            "нажимать несколько раз, если сумма покупки не равна ни одной кнопке. Когда всё набрано — нажмите "
            "«Начислить N баллов». Если покупатель новый, бот сразу пришлёт QR-код и ссылку — отправьте её "
            "клиенту, чтобы он привязал бота к своей карте и видел баллы у себя.\n\n"
            "<b>➕ Добавить магазин</b> — открыть ещё одну точку под вашим поставщиком, с QR-кодом для нового "
            "продавца этой точки.\n\n"
            "<b>➕ Добавить клиента</b> — просто зарегистрировать покупателя в программе лояльности (без баллов), "
            "если он ещё не совершал покупку, но хочет получить карту.\n\n"
            "<b>🆘 Поддержка</b> — связаться с Miramax по любым вопросам.\n"
            "<b>🌐 Язык</b> — сменить язык интерфейса."
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
        "help_seller": "Siz — Sotuvchi. To'liq yo'riqnoma — «ℹ️ Ma'lumot» tugmasida.",
        "menu_bonus_site": "🎁 Bonus",
        "bonus_site_text": "Miramax Bonus: {link}",
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
        "ask_store_phone": "Do'kon telefon raqami (mijozlar uchun «Do'konga qo'ng'iroq» tugmasi)?",
        "store_created": (
            "«{store_name}» ({city}) do'koni qo'shildi.\n"
            "Sotuvchi: {first_name} {last_name}.\n\n"
            "Bu QR yoki havolani sotuvchiga yuboring — ochilgach, u darhol shu do'konga bog'lanadi:\n{link}"
        ),
        "analytics_empty": "Hozircha do'kon yo'q — do'kon qo'shilgach analitika paydo bo'ladi.",
        "analytics_header": "«{supplier_name}», do'konlar: {store_count}",
        "analytics_line": "• {store_name}: sotuvlar — {total_sales}, qo'shilgan ball — {total_points_issued}",
        "seller_menu_issue_points": "💳 Ball berish",
        "seller_menu_add_client": "➕ Mijoz qo'shish",
        "seller_menu_info": "ℹ️ Ma'lumot",
        "seller_menu_support": "🆘 Yordam",
        "no_store_link": "Sizning hisobingiz do'konga bog'lanmagan.",
        "ask_client_first_name": "Xaridorning ismi?",
        "ask_client_last_name": "Xaridorning familiyasi?",
        "ask_client_phone": "Xaridorning telefon raqami?",
        "new_customer_invite_caption": (
            "Bu xaridor hali botni ochmagan. Unga shu havola/QR-ni yuboring — "
            "ochgach, u darhol o'z ballarini ko'radi:\n{link}"
        ),
        "match_list_header": "Bir nechta mos keldi — birini tanlang:",
        "match_list_line": "{name} — {phone}",
        "match_create_new": "➕ Yangi xaridor",
        "client_registered": "«{name}» xaridori ro'yxatga olindi.",
        "client_not_found_confirm": "⚠️ Bu raqamli xaridor topilmadi. Yangi xaridor qo'shilsinmi?",
        "confirm_yes": "✅ Ha",
        "confirm_no": "❌ Yo'q",
        "tier_compose_header": "Xarid summasini tanlang (bir necha marta bosishingiz mumkin):",
        "tier_compose_line": "{tier} so'm × {qty}",
        "tier_compose_total": "Xarid summasi: {amount} so'm",
        "tier_reset_button": "🔄 Bekor qilish",
        "tier_confirm_button": "✅ {points} ball qo'shish",
        "tier_not_configured": "Bu summa uchun ball hali sozlanmagan. Administratorga murojaat qiling.",
        "tier_not_configured_button": "⚠️ Ball sozlanmagan",
        "tier_sale_confirmed": "«{name}» xaridoriga {points} ball qo'shildi.",
        "submenu_back": "⬅️ Orqaga",
        "cancel_action": "❌ Amalni bekor qilish",
        "info_text": (
            "<b>Miramax Bonus botidan qanday foydalanish</b>\n\n"
            "<b>💳 Ball berish</b> — asosiy amal. Xaridorning ismi, familiyasi va telefonini kiritasiz. "
            "Agar bu xaridor bazada bo'lsa — bot o'zi topadi (yoki bir nechta mos kelsa, tanlashni so'raydi). "
            "Keyin xarid summasi kartalarini bosing — har bir summaga bitta bosish, bir nechta marta bosish "
            "mumkin, agar xarid summasi tugmalardan biriga teng bo'lmasa. Barchasi tanlangach — «N ball "
            "qo'shish» tugmasini bosing. Agar xaridor yangi bo'lsa, bot darhol QR-kod va havola yuboradi — "
            "uni mijozga yuboring, shunda u botni o'z kartasiga bog'lab, ballarini ko'ra oladi.\n\n"
            "<b>➕ Do'kon qo'shish</b> — yetkazib beruvchingiz ostida yana bitta nuqta ochish, shu nuqtaning "
            "yangi sotuvchisi uchun QR bilan.\n\n"
            "<b>➕ Mijoz qo'shish</b> — xaridorni sodiqlik dasturiga oddiy ro'yxatga olish (ballarsiz), agar u "
            "hali xarid qilmagan bo'lsa-yu, karta olishni istasa.\n\n"
            "<b>🆘 Yordam</b> — har qanday savol bo'yicha Miramax bilan bog'lanish.\n"
            "<b>🌐 Til</b> — interfeys tilini almashtirish."
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
        "help_seller": "Siz — Satıcısınız. Tam kılavuz — «ℹ️ Bilgi» düğmesinde.",
        "menu_bonus_site": "🎁 Bonus",
        "bonus_site_text": "Miramax Bonus: {link}",
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
        "ask_store_phone": "Mağaza telefon numarası (müşteriler için «Mağazayı ara» butonu)?",
        "store_created": (
            "«{store_name}» ({city}) mağazası eklendi.\n"
            "Satıcı: {first_name} {last_name}.\n\n"
            "Bu QR'ı veya bağlantıyı satıcıya gönderin — açıldığında hemen bu mağazaya bağlanır:\n{link}"
        ),
        "analytics_empty": "Henüz mağaza yok — mağaza eklendikten sonra analiz görünecek.",
        "analytics_header": "«{supplier_name}», mağazalar: {store_count}",
        "analytics_line": "• {store_name}: satışlar — {total_sales}, yüklenen puan — {total_points_issued}",
        "seller_menu_issue_points": "💳 Puan ver",
        "seller_menu_add_client": "➕ Müşteri ekle",
        "seller_menu_info": "ℹ️ Bilgi",
        "seller_menu_support": "🆘 Destek",
        "no_store_link": "Hesabınız bir mağazaya bağlı değil.",
        "ask_client_first_name": "Müşterinin adı?",
        "ask_client_last_name": "Müşterinin soyadı?",
        "ask_client_phone": "Müşterinin telefon numarası?",
        "new_customer_invite_caption": (
            "Bu müşteri botu henüz açmadı. Bu bağlantıyı/QR'ı gönderin — "
            "açtığında puanlarını hemen görür:\n{link}"
        ),
        "match_list_header": "Birden fazla eşleşme bulundu — birini seçin:",
        "match_list_line": "{name} — {phone}",
        "match_create_new": "➕ Yeni müşteri",
        "client_registered": "«{name}» müşterisi kaydedildi.",
        "client_not_found_confirm": "⚠️ Bu numaraya sahip müşteri bulunamadı. Yeni müşteri eklensin mi?",
        "confirm_yes": "✅ Evet",
        "confirm_no": "❌ Hayır",
        "tier_compose_header": "Satış tutarını seçin (birden fazla kez basabilirsiniz):",
        "tier_compose_line": "{tier} sum × {qty}",
        "tier_compose_total": "Satış tutarı: {amount} sum",
        "tier_reset_button": "🔄 Sıfırla",
        "tier_confirm_button": "✅ {points} puan yükle",
        "tier_not_configured": "Bu tutar için puan henüz ayarlanmadı. Yöneticiyle iletişime geçin.",
        "tier_not_configured_button": "⚠️ Puan ayarlanmadı",
        "tier_sale_confirmed": "«{name}» müşterisine {points} puan yüklendi.",
        "submenu_back": "⬅️ Geri",
        "cancel_action": "❌ İşlemi iptal et",
        "info_text": (
            "<b>Miramax Bonus botu nasıl kullanılır</b>\n\n"
            "<b>💳 Puan ver</b> — ana işlem. Müşterinin adını, soyadını ve telefonunu girin. Bu müşteri "
            "zaten sistemdeyse bot onu kendisi bulur (birden fazla eşleşme varsa seçmenizi ister). Ardından "
            "satış tutarı kartlarına basın — her tutar için bir basış, tutar hiçbir düğmeye eşit değilse "
            "birden fazla kez basabilirsiniz. Hepsi seçildiğinde «N puan yükle» düğmesine basın. Müşteri "
            "yeniyse bot hemen bir QR kod ve bağlantı gönderir — bunu müşteriye iletin, böylece botu kendi "
            "kartına bağlayıp puanlarını görebilir.\n\n"
            "<b>➕ Mağaza ekle</b> — tedarikçiniz altında yeni bir nokta açın, bu noktanın yeni satıcısı "
            "için QR ile.\n\n"
            "<b>➕ Müşteri ekle</b> — henüz satın alma yapmamış ama kart almak isteyen müşteriyi puansız "
            "olarak sadakat programına kaydedin.\n\n"
            "<b>🆘 Destek</b> — her türlü soru için Miramax ile iletişime geçin.\n"
            "<b>🌐 Dil</b> — arayüz dilini değiştirin."
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
