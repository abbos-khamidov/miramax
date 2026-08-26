LANGS = ("ru", "uz", "tr")
DEFAULT_LANG = "ru"

LANGUAGE_LABELS = {
    "ru": "🇷🇺 Русский",
    "uz": "🇺🇿 Oʻzbekcha",
    "tr": "🇹🇷 Türkçe",
}
LANGUAGE_CODE_BY_LABEL = {label: code for code, label in LANGUAGE_LABELS.items()}

CHOOSE_LANGUAGE_FIRST_RUN = "Выберите язык интерфейса:\nTilni tanlang:\nDil seçin:"

# Shown once on first /start, before the language is known — brief, all three languages at once.
FIRST_RUN_INSTRUCTION = (
    "<b>Miramax Bonus — бот Завода</b>\n"
    "Здесь можно:\n"
    "• добавлять Админов, Поставщиков и Оптовиков — сразу выдаётся QR-код для входа\n"
    "• смотреть список и карточки поставщиков/оптовиков/админов, искать по телефону\n"
    "• смотреть аналитику по всей сети\n\n"
    "<b>Miramax Bonus — Zavod boti</b>\n"
    "Bu yerda:\n"
    "• Admin, Yetkazib beruvchi va Optoviklarni qo'shish — darhol kirish uchun QR-kod beriladi\n"
    "• yetkazib beruvchilar/optoviklar/adminlar ro'yxati va kartochkalarini ko'rish, telefon bo'yicha qidirish\n"
    "• butun tarmoq bo'yicha analitikani ko'rish\n\n"
    "<b>Miramax Bonus — Fabrika botu</b>\n"
    "Burada:\n"
    "• Admin, Tedarikçi ve Toptancı ekleyebilirsiniz — giriş için hemen QR kod verilir\n"
    "• tedarikçi/toptancı/admin listelerini ve kartlarını görebilir, telefonla arayabilirsiniz\n"
    "• tüm ağın analizini görebilirsiniz"
)

# Telegram profile texts (shown before the user even presses Start) — keyed by Telegram
# client language_code. Most of the target audience runs Uzbek content on a phone whose
# Telegram UI language isn't necessarily set to "uz", so Uzbek is the default/fallback
# (None) rather than Russian — Russian is served only to clients explicitly reporting "ru".
PROFILE_DESCRIPTIONS: dict[str | None, str] = {
    None: (
        "Miramax Bonus — Zavod boti. Admin, Yetkazib beruvchi va Optoviklarni qo'shing, "
        "butun tarmoq bo'yicha analitikani ko'ring. Faqat Zavod jamoasi uchun.\n\n"
        "Boshlash uchun «Start» tugmasini bosing."
    ),
    "ru": (
        "Miramax Bonus — бот Завода. Добавляйте Админов, Поставщиков и Оптовиков, "
        "смотрите аналитику по всей сети. Доступ только для команды Завода.\n\n"
        "Нажмите «Старт», чтобы начать."
    ),
    "tr": (
        "Miramax Bonus — Fabrika botu. Admin, Tedarikçi ve Toptancı ekleyin, "
        "tüm ağın analizini görüntüleyin. Yalnızca Fabrika ekibi içindir.\n\n"
        "Başlamak için «Start»a basın."
    ),
    "en": (
        "Miramax Bonus — Factory bot. Add Admins, Suppliers and Wholesalers, "
        "view network-wide analytics. Access is limited to the Factory team.\n\n"
        "Press Start to begin."
    ),
}

PROFILE_SHORT_DESCRIPTIONS: dict[str | None, str] = {
    None: "Miramax Bonus tarmog'ini boshqarish paneli — Zavod jamoasi uchun. Boshlash uchun «Start» tugmasini bosing.",
    "ru": "Панель управления сетью Miramax Bonus для команды Завода. Нажмите «Старт», чтобы начать.",
    "tr": "Miramax Bonus ağını yönetme paneli — Fabrika ekibi için. Başlamak için «Start»a basın.",
    "en": "Manage the Miramax Bonus network — for the Factory team. Press Start to begin.",
}

TRANSLATIONS: dict[str, dict[str, str]] = {
    "ru": {
        "choose_language": "Выберите язык интерфейса:",
        "language_saved": "Готово, дальше буду писать по-русски.",
        "welcome_instruction": (
            "Это бот Завода Miramax Bonus.\n\n"
            "• «➕ Добавить нового пользователя» — завести Админа, Поставщика или Оптовика. "
            "Для Поставщика/Оптовика вводите имя, фамилию, телефон, название компании и город — "
            "бот сразу выдаёт QR-код. Отправьте его — открыв QR (в боте для поставщиков), "
            "человек автоматически попадёт в свой кабинет, ничего вводить самому не нужно.\n"
            "• «📊 Открыть аналитику» — сводка по всей сети: поставщики, магазины, продажи.\n"
            "• «🌐 Язык» — сменить язык в любой момент."
        ),
        "no_access": "Доступ не назначен. Обратитесь к администратору Miramax.",
        "no_permission": "У вас нет прав для этого действия.",
        "invite_not_found": "Приглашение не найдено. Уточните ссылку у того, кто его выдал.",
        "invite_already_used": "Это приглашение уже использовано.",
        "invite_wrong_role": "У вашего аккаунта уже назначена роль «{role}» — это приглашение для неё не применяется.",
        "admin_redeemed": "Готово — вы назначены Админом Miramax Bonus.",
        "menu_add_user": "➕ Добавить нового пользователя",
        "menu_analytics": "📊 Открыть аналитику",
        "menu_points_rate": "💱 Курс баллов",
        "menu_online_showcase": "🛍 Онлайн витрина",
        "online_showcase_text": "Онлайн-витрина товаров для покупателей:\n{link}",
        "menu_language": "🌐 Язык",
        "points_rate_current": "Сейчас: {sum_per_point} сум = 1 балл.\nВведите новое значение — сколько сум за 1 балл:",
        "points_rate_invalid": "Введите целое положительное число.",
        "points_rate_saved": "Готово: теперь {sum_per_point} сум = 1 балл. Действует для новых покупок, старые начисления не пересчитываются.",
        "ask_product_photo": "Отправьте фото товара.",
        "set_tier_usage": "Формат: /set_tier <номинал> <баллы>, например /set_tier 300000 21",
        "set_tier_invalid": "Номинал и баллы должны быть числами, баллы \u2265 0.",
        "set_tier_not_found": "Номинал {tier} не найден в списке кнопок сумм.",
        "set_tier_saved": "Готово: {tier} сум \u2192 {points} баллов.",
        "show_tiers_empty": "Номиналы ещё не настроены.",
        "show_tiers_header": "Кнопки сумм у продавцов:",
        "ask_product_photo_invalid": "Нужно отправить фото, не текст.",
        "ask_product_category": "Категория товара?",
        "ask_product_name": "Название товара?",
        "ask_product_points_cost": "Сколько баллов стоит товар?",
        "points_cost_invalid": "Введите целое положительное число баллов.",
        "product_created": "Товар «{name}» ({category}) добавлен — {points_cost} баллов. Уже виден клиентам в каталоге.",
        "submenu_admin": "👤 Админ",
        "submenu_wholesaler": "🏬 Магазин",
        "submenu_back": "⬅️ Назад",
        "choose_user_type": "Кого добавляем?",
        "ask_first_name": "Имя контактного лица?",
        "ask_last_name": "Фамилия?",
        "ask_phone": "Номер телефона?",
        "ask_company_name": "Название компании?",
        "ask_city": "Город?",
        "admin_created": (
            "Новый Админ: {first_name} {last_name}, {phone}.\n\n"
            "Отправьте этот QR или ссылку — открыв её в этом же боте, человек сразу станет Админом:\n{link}"
        ),
        "supplier_created": (
            "{kind_label} «{company_name}» ({city}) создан.\n"
            "Контакт: {first_name} {last_name}, {phone}.\n\n"
            "Отправьте этот QR или ссылку — открыв её, человек сразу попадёт в свой кабинет в боте:\n{link}"
        ),
        "kind_supplier": "Поставщик",
        "kind_wholesaler": "Магазин",
        "analytics_no_suppliers": "Поставщиков пока нет — добавьте первого через «➕ Добавить нового пользователя».",
        "analytics_header": "<b>Сеть Miramax</b>: поставщиков — {supplier_count}, магазинов — {store_count}\n",
        "analytics_supplier_line": "🏭 <b>{supplier_name}</b> — магазинов: {store_count}",
        "analytics_store_line": "   • {store_name}: продаж — {total_sales}, баллов начислено — {total_points_issued}",
        "analytics_store_line_empty": "   (магазинов пока нет)",
        "menu_view_users": "👥 Посмотреть пользователей",
        "view_admins": "👤 Админы",
        "view_suppliers": "🚚 Поставщики",
        "view_wholesalers": "📦 Оптовики",
        "view_search": "🔎 Поиск по базе",
        "choose_view_type": "Кого смотрим?",
        "ask_search_phone": "Введите номер телефона для поиска:",
        "search_not_found": "Никого не нашли по этому номеру.",
        "empty_list": "Пока никого нет в этом разделе.",
        "entity_list_header": "Нашлось: {count}. Выберите из списка или найдите по номеру.",
        "admin_detail": "👤 Админ\nИмя: {name}\nТелефон: {phone}\nTelegram ID: {telegram_id}",
        "supplier_detail": (
            "{kind_label} «{company_name}»\n"
            "Город: {city}\n"
            "Контакт: {first_name} {last_name}, {phone}\n\n"
            "Магазинов: {store_count}\n"
            "Покупок всего: {total_purchases}\n"
            "Баллов начислено всего: {total_points}"
        ),
    },
    "uz": {
        "choose_language": "Interfeys tilini tanlang:",
        "language_saved": "Tayyor, endi o'zbek tilida yozaman.",
        "welcome_instruction": (
            "Bu Miramax Bonus Zavod boti.\n\n"
            "• «➕ Yangi foydalanuvchi qo'shish» — Admin, Yetkazib beruvchi yoki Optovik qo'shish. "
            "Yetkazib beruvchi/Optovik uchun ism, familiya, telefon, kompaniya nomi va shaharni kiriting — "
            "bot darhol QR-kod beradi. Uni yuboring — QR ochilgach (yetkazib beruvchilar boti orqali) "
            "odam avtomatik ravishda o'z kabinetiga tushadi, hech narsa qo'lda kiritish shart emas.\n"
            "• «📊 Analitikani ochish» — butun tarmoq bo'yicha hisobot: yetkazib beruvchilar, do'konlar, sotuvlar.\n"
            "• «🌐 Til» — istalgan vaqtda tilni almashtirish."
        ),
        "no_access": "Sizga ruxsat berilmagan. Miramax administratoriga murojaat qiling.",
        "no_permission": "Bu amal uchun ruxsatingiz yo'q.",
        "invite_not_found": "Taklifnoma topilmadi. Havolani bergan shaxsdan aniqlashtiring.",
        "invite_already_used": "Bu taklifnoma allaqachon ishlatilgan.",
        "invite_wrong_role": "Sizning hisobingizga allaqachon «{role}» roli belgilangan — bu taklifnoma unga tegishli emas.",
        "admin_redeemed": "Tayyor — sizga Miramax Bonus Admin roli berildi.",
        "menu_add_user": "➕ Yangi foydalanuvchi qo'shish",
        "menu_analytics": "📊 Analitikani ochish",
        "menu_points_rate": "💱 Ball kursi",
        "menu_online_showcase": "🛍 Onlayn vitrina",
        "online_showcase_text": "Xaridorlar uchun onlayn vitrina:\n{link}",
        "menu_language": "🌐 Til",
        "points_rate_current": "Hozir: {sum_per_point} so'm = 1 ball.\nYangi qiymatni kiriting — 1 ball uchun necha so'm:",
        "points_rate_invalid": "Butun musbat son kiriting.",
        "points_rate_saved": "Tayyor: endi {sum_per_point} so'm = 1 ball. Yangi xaridlar uchun ishlaydi, eski yozuvlar qayta hisoblanmaydi.",
        "ask_product_photo": "Tovar rasmini yuboring.",
        "set_tier_usage": "Format: /set_tier <nominal> <ball>, masalan /set_tier 300000 21",
        "set_tier_invalid": "Nominal va ball raqam bo'lishi kerak, ball \u2265 0.",
        "set_tier_not_found": "{tier} nominali summalar tugmalari ro'yxatida topilmadi.",
        "set_tier_saved": "Tayyor: {tier} so'm \u2192 {points} ball.",
        "show_tiers_empty": "Nominallar hali sozlanmagan.",
        "show_tiers_header": "Sotuvchilardagi summa tugmalari:",
        "ask_product_photo_invalid": "Matn emas, rasm yuborish kerak.",
        "ask_product_category": "Tovar kategoriyasi?",
        "ask_product_name": "Tovar nomi?",
        "ask_product_points_cost": "Tovar necha ball turadi?",
        "points_cost_invalid": "Butun musbat ball sonini kiriting.",
        "product_created": "«{name}» ({category}) tovari qo'shildi — {points_cost} ball. Mijozlar katalogida darhol ko'rinadi.",
        "submenu_admin": "👤 Admin",
        "submenu_wholesaler": "🏬 Do'kon",
        "submenu_back": "⬅️ Orqaga",
        "choose_user_type": "Kimni qo'shamiz?",
        "ask_first_name": "Kontakt shaxsning ismi?",
        "ask_last_name": "Familiyasi?",
        "ask_phone": "Telefon raqami?",
        "ask_company_name": "Kompaniya nomi?",
        "ask_city": "Shahar?",
        "admin_created": (
            "Yangi Admin: {first_name} {last_name}, {phone}.\n\n"
            "Bu QR yoki havolani yuboring — shu botda ochilgach, odam darhol Admin bo'ladi:\n{link}"
        ),
        "supplier_created": (
            "{kind_label} «{company_name}» ({city}) yaratildi.\n"
            "Kontakt: {first_name} {last_name}, {phone}.\n\n"
            "Bu QR yoki havolani yuboring — ochilgach, odam darhol o'z kabinetiga tushadi:\n{link}"
        ),
        "kind_supplier": "Yetkazib beruvchi",
        "kind_wholesaler": "Do'kon",
        "analytics_no_suppliers": "Hozircha yetkazib beruvchilar yo'q — «➕ Yangi foydalanuvchi qo'shish» orqali birinchisini qo'shing.",
        "analytics_header": "<b>Miramax tarmog'i</b>: yetkazib beruvchilar — {supplier_count}, do'konlar — {store_count}\n",
        "analytics_supplier_line": "🏭 <b>{supplier_name}</b> — do'konlar: {store_count}",
        "analytics_store_line": "   • {store_name}: sotuvlar — {total_sales}, ball qo'shildi — {total_points_issued}",
        "analytics_store_line_empty": "   (hozircha do'konlar yo'q)",
        "menu_view_users": "👥 Foydalanuvchilarni ko'rish",
        "view_admins": "👤 Adminlar",
        "view_suppliers": "🚚 Yetkazib beruvchilar",
        "view_wholesalers": "📦 Optoviklar",
        "view_search": "🔎 Bazadan qidirish",
        "choose_view_type": "Kimni ko'ramiz?",
        "ask_search_phone": "Qidirish uchun telefon raqamini kiriting:",
        "search_not_found": "Bu raqam bo'yicha hech kim topilmadi.",
        "empty_list": "Bu bo'limda hozircha hech kim yo'q.",
        "entity_list_header": "Topildi: {count}. Ro'yxatdan tanlang yoki raqam bo'yicha qidiring.",
        "admin_detail": "👤 Admin\nIsmi: {name}\nTelefon: {phone}\nTelegram ID: {telegram_id}",
        "supplier_detail": (
            "{kind_label} «{company_name}»\n"
            "Shahar: {city}\n"
            "Kontakt: {first_name} {last_name}, {phone}\n\n"
            "Do'konlar: {store_count}\n"
            "Jami xaridlar: {total_purchases}\n"
            "Jami qo'shilgan ball: {total_points}"
        ),
    },
    "tr": {
        "choose_language": "Arayüz dilini seçin:",
        "language_saved": "Tamam, bundan sonra Türkçe yazacağım.",
        "welcome_instruction": (
            "Bu Miramax Bonus Fabrika botudur.\n\n"
            "• «➕ Yeni kullanıcı ekle» — Admin, Tedarikçi veya Toptancı ekleyin. "
            "Tedarikçi/Toptancı için ad, soyad, telefon, şirket adı ve şehir girin — "
            "bot hemen bir QR kod verir. Bunu gönderin — QR açıldığında (tedarikçi botunda) "
            "kişi otomatik olarak kendi paneline geçer, hiçbir şey elle girmesi gerekmez.\n"
            "• «📊 Analizi aç» — tüm ağın özeti: tedarikçiler, mağazalar, satışlar.\n"
            "• «🌐 Dil» — dili istediğiniz zaman değiştirin."
        ),
        "no_access": "Erişim tanımlanmamış. Miramax yöneticisiyle iletişime geçin.",
        "no_permission": "Bu işlem için yetkiniz yok.",
        "invite_not_found": "Davet bulunamadı. Bağlantıyı verenle teyit edin.",
        "invite_already_used": "Bu davet zaten kullanılmış.",
        "invite_wrong_role": "Hesabınıza zaten «{role}» rolü atanmış — bu davet ona uygulanmaz.",
        "admin_redeemed": "Tamamlandı — Miramax Bonus Admin rolü size atandı.",
        "menu_add_user": "➕ Yeni kullanıcı ekle",
        "menu_analytics": "📊 Analizi aç",
        "menu_points_rate": "💱 Puan kuru",
        "menu_online_showcase": "🛍 Online vitrin",
        "online_showcase_text": "Müşteriler için online vitrin:\n{link}",
        "menu_language": "🌐 Dil",
        "points_rate_current": "Şu an: {sum_per_point} so'm = 1 puan.\nYeni değeri girin — 1 puan için kaç so'm:",
        "points_rate_invalid": "Pozitif bir tam sayı girin.",
        "points_rate_saved": "Tamam: artık {sum_per_point} so'm = 1 puan. Yeni satışlar için geçerli, eski kayıtlar yeniden hesaplanmaz.",
        "ask_product_photo": "Ürün fotoğrafını gönderin.",
        "set_tier_usage": "Format: /set_tier <tutar> <puan>, örnek /set_tier 300000 21",
        "set_tier_invalid": "Tutar ve puan sayı olmalı, puan \u2265 0.",
        "set_tier_not_found": "{tier} tutarı miktar düğmeleri listesinde bulunamadı.",
        "set_tier_saved": "Tamam: {tier} sum \u2192 {points} puan.",
        "show_tiers_empty": "Tutarlar henüz ayarlanmadı.",
        "show_tiers_header": "Satıcılardaki tutar düğmeleri:",
        "ask_product_photo_invalid": "Metin değil, fotoğraf göndermeniz gerekiyor.",
        "ask_product_category": "Ürün kategorisi?",
        "ask_product_name": "Ürün adı?",
        "ask_product_points_cost": "Ürün kaç puan?",
        "points_cost_invalid": "Pozitif bir tam puan sayısı girin.",
        "product_created": "«{name}» ({category}) ürünü eklendi — {points_cost} puan. Müşterilerin kataloğunda hemen görünür.",
        "submenu_admin": "👤 Admin",
        "submenu_wholesaler": "🏬 Mağaza",
        "submenu_back": "⬅️ Geri",
        "choose_user_type": "Kimi ekliyoruz?",
        "ask_first_name": "İlgili kişinin adı?",
        "ask_last_name": "Soyadı?",
        "ask_phone": "Telefon numarası?",
        "ask_company_name": "Şirket adı?",
        "ask_city": "Şehir?",
        "admin_created": (
            "Yeni Admin: {first_name} {last_name}, {phone}.\n\n"
            "Bu QR'ı veya bağlantıyı gönderin — aynı botta açıldığında kişi hemen Admin olur:\n{link}"
        ),
        "supplier_created": (
            "{kind_label} «{company_name}» ({city}) oluşturuldu.\n"
            "İletişim: {first_name} {last_name}, {phone}.\n\n"
            "Bu QR'ı veya bağlantıyı gönderin — açıldığında kişi hemen kendi paneline geçer:\n{link}"
        ),
        "kind_supplier": "Tedarikçi",
        "kind_wholesaler": "Mağaza",
        "analytics_no_suppliers": "Henüz tedarikçi yok — «➕ Yeni kullanıcı ekle» ile ilkini ekleyin.",
        "analytics_header": "<b>Miramax ağı</b>: tedarikçiler — {supplier_count}, mağazalar — {store_count}\n",
        "analytics_supplier_line": "🏭 <b>{supplier_name}</b> — mağazalar: {store_count}",
        "analytics_store_line": "   • {store_name}: satışlar — {total_sales}, eklenen puan — {total_points_issued}",
        "analytics_store_line_empty": "   (henüz mağaza yok)",
        "menu_view_users": "👥 Kullanıcıları görüntüle",
        "view_admins": "👤 Adminler",
        "view_suppliers": "🚚 Tedarikçiler",
        "view_wholesalers": "📦 Toptancılar",
        "view_search": "🔎 Veritabanında ara",
        "choose_view_type": "Kimi görüntülüyoruz?",
        "ask_search_phone": "Aramak için telefon numarasını girin:",
        "search_not_found": "Bu numarayla kimse bulunamadı.",
        "empty_list": "Bu bölümde henüz kimse yok.",
        "entity_list_header": "Bulunan: {count}. Listeden seçin veya numarayla arayın.",
        "admin_detail": "👤 Admin\nAdı: {name}\nTelefon: {phone}\nTelegram ID: {telegram_id}",
        "supplier_detail": (
            "{kind_label} «{company_name}»\n"
            "Şehir: {city}\n"
            "İletişim: {first_name} {last_name}, {phone}\n\n"
            "Mağazalar: {store_count}\n"
            "Toplam satış: {total_purchases}\n"
            "Toplam eklenen puan: {total_points}"
        ),
    },
}


def t(lang: str | None, key: str, **kwargs) -> str:
    lang = lang if lang in TRANSLATIONS else DEFAULT_LANG
    text = TRANSLATIONS[lang][key]
    return text.format(**kwargs) if kwargs else text


def all_variants(key: str) -> set[str]:
    return {TRANSLATIONS[lang][key] for lang in LANGS}
