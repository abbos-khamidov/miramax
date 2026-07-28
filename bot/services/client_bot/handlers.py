from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, Message, User
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.models import CustomerCard, InviteTargetRole, PointsTransaction, Product, Redemption, RedemptionStatus, Store
from core.services import invites as invites_service
from core.services import redemptions as redemptions_service
from services.client_bot.i18n import (
    CHOOSE_LANGUAGE_FIRST_RUN,
    DEFAULT_LANG,
    LANGUAGE_CODE_BY_LABEL,
    LANGUAGE_LABELS,
    t,
)
from core.config import settings
from services.client_bot.keyboards import (
    BALANCE_LABELS,
    CALL_STORE_LABELS,
    HISTORY_LABELS,
    INFO_LABELS,
    LANGUAGE_MENU_LABELS,
    PRODUCTS_LABELS,
    REDEEM_LABELS,
    SEARCH_LABELS,
    call_store_keyboard,
    catalog_webapp_keyboard,
    customer_menu,
    language_menu,
)
from services.client_bot.states import SearchProductForm

router = Router(name="client")

PRODUCTS_PAGE_SIZE = 10


def _full_name_from_user(user: User | None) -> str | None:
    if user is None:
        return None
    return " ".join(part for part in [user.first_name, user.last_name] if part) or user.username


def _full_name(message: Message) -> str | None:
    return _full_name_from_user(message.from_user)


async def _get_or_create_customer_by_id(session: AsyncSession, telegram_id: int, full_name: str | None) -> CustomerCard:
    result = await session.execute(select(CustomerCard).where(CustomerCard.telegram_id == telegram_id))
    customer = result.scalar_one_or_none()
    if customer is None:
        customer = CustomerCard(telegram_id=telegram_id, full_name=full_name)
        session.add(customer)
        await session.commit()
        await session.refresh(customer)
    elif full_name and customer.full_name != full_name:
        customer.full_name = full_name
        await session.commit()
        await session.refresh(customer)
    return customer


async def _get_or_create_customer(session: AsyncSession, message: Message) -> CustomerCard:
    return await _get_or_create_customer_by_id(session, message.from_user.id, _full_name(message))


async def _customer_balance(session: AsyncSession, customer_id: int) -> int:
    earned_result = await session.execute(
        select(func.coalesce(func.sum(PointsTransaction.points), 0)).where(
            PointsTransaction.customer_id == customer_id
        )
    )
    spent_result = await session.execute(
        select(func.coalesce(func.sum(Redemption.points_spent), 0)).where(
            Redemption.customer_id == customer_id,
            Redemption.status == RedemptionStatus.FULFILLED,
        )
    )
    return int(earned_result.scalar_one() or 0) - int(spent_result.scalar_one() or 0)


def _points(value: int) -> str:
    return f"{value:,}".replace(",", " ")


def _product_lines(products: list[Product], start: int = 1) -> str:
    if not products:
        return "Katalogda hozircha faol tovar yo'q."
    lines = []
    for index, product in enumerate(products, start=start):
        icon = product.icon_or_image_url if product.icon_or_image_url and not product.icon_or_image_url.startswith("http") else "•"
        lines.append(f"{index}. {icon} <b>{product.name}</b>\n   {product.category} · {_points(product.points_cost)} ball")
    return "\n".join(lines)


async def _product_count(session: AsyncSession) -> int:
    result = await session.execute(select(func.count(Product.id)).where(Product.active.is_(True)))
    return int(result.scalar_one() or 0)


async def _product_page(session: AsyncSession, page: int) -> tuple[list[Product], int]:
    total = await _product_count(session)
    max_page = max((total - 1) // PRODUCTS_PAGE_SIZE, 0)
    page = min(max(page, 0), max_page)
    result = await session.execute(
        select(Product)
        .where(Product.active.is_(True))
        .order_by(Product.category, Product.name)
        .offset(page * PRODUCTS_PAGE_SIZE)
        .limit(PRODUCTS_PAGE_SIZE)
    )
    return list(result.scalars().all()), total


async def _product_by_position(session: AsyncSession, position: int) -> tuple[Product | None, int, int]:
    total = await _product_count(session)
    if total == 0:
        return None, 0, 0
    position = min(max(position, 0), total - 1)
    result = await session.execute(
        select(Product)
        .where(Product.active.is_(True))
        .order_by(Product.category, Product.name)
        .offset(position)
        .limit(1)
    )
    return result.scalar_one_or_none(), position, total


def _products_keyboard(products: list[Product], page: int, total: int) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=f"Подробнее: {product.name[:30]}", callback_data=f"product:{product.id}:{page}")]
        for product in products
    ]
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️ Пред", callback_data=f"products_page:{page - 1}"))
    if (page + 1) * PRODUCTS_PAGE_SIZE < total:
        nav.append(InlineKeyboardButton(text="След ➡️", callback_data=f"products_page:{page + 1}"))
    if nav:
        rows.append(nav)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _carousel_keyboard(lang: str, position: int, total: int, product_id: int) -> InlineKeyboardMarkup:
    prev_pos = max(position - 1, 0)
    next_pos = min(position + 1, max(total - 1, 0))
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⬅️ Пред", callback_data=f"carousel:{prev_pos}"),
                InlineKeyboardButton(text=f"{position + 1}/{total}", callback_data="noop"),
                InlineKeyboardButton(text="След ➡️", callback_data=f"carousel:{next_pos}"),
            ],
            [InlineKeyboardButton(text="Подробнее", callback_data=f"product:{product_id}:{position}")],
            [InlineKeyboardButton(text=t(lang, "product_redeem_button"), callback_data=f"redeem:{product_id}:{position}")],
        ]
    )


def _carousel_text(product: Product, position: int, total: int) -> str:
    return (
        f"<b>{product.name}</b>\n"
        f"{position + 1}/{total}\n\n"
        f"Kategoriya: {product.category}\n"
        f"Narxi: <b>{_points(product.points_cost)} ball</b>"
    )


def _product_detail_text(product: Product) -> str:
    return (
        f"<b>{product.name}</b>\n\n"
        f"Kategoriya: {product.category}\n"
        f"Narxi: <b>{_points(product.points_cost)} ball</b>\n\n"
        "Tavsif: bu yerga mahsulot haqida batafsil ma'lumot qo'shiladi."
    )


def _product_detail_keyboard(lang: str, position: int, product_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "product_redeem_button"), callback_data=f"redeem:{product_id}:{position}")],
            [InlineKeyboardButton(text="⬅️ Katalogga qaytish", callback_data=f"carousel:{position}")],
        ]
    )


async def _send_menu(message: Message, session: AsyncSession, customer: CustomerCard) -> None:
    lang = customer.language or DEFAULT_LANG
    balance = await _customer_balance(session, customer.id)
    text = t(lang, "start_greeting") + "\n\n" + t(lang, "balance_label", balance=_points(balance))
    await message.answer(text, reply_markup=customer_menu(lang))


@router.message(CommandStart(deep_link=True))
async def start_with_payload(message: Message, command: CommandObject, session: AsyncSession) -> None:
    payload = command.args or ""
    if payload.startswith("inv_"):
        await _handle_invite_redemption(message, session, payload)
        return
    await start_plain(message, session)


@router.message(CommandStart())
async def start_plain(message: Message, session: AsyncSession) -> None:
    customer = await _get_or_create_customer(session, message)
    if customer.language is None:
        await message.answer(CHOOSE_LANGUAGE_FIRST_RUN, reply_markup=language_menu())
        return
    await _send_menu(message, session, customer)


@router.message(F.text.in_(LANGUAGE_LABELS.values()))
async def language_chosen(message: Message, session: AsyncSession) -> None:
    customer = await _get_or_create_customer(session, message)
    lang = LANGUAGE_CODE_BY_LABEL[message.text]
    customer.language = lang
    await session.commit()
    await message.answer(t(lang, "language_saved"))
    await _send_menu(message, session, customer)


@router.message(F.text.in_(LANGUAGE_MENU_LABELS))
async def language_menu_button(message: Message, session: AsyncSession) -> None:
    customer = await _get_or_create_customer(session, message)
    lang = customer.language or DEFAULT_LANG
    await message.answer(t(lang, "choose_language"), reply_markup=language_menu())


async def _handle_invite_redemption(message: Message, session: AsyncSession, code: str) -> None:
    try:
        invite = await invites_service.redeem_invite(session, code, message.from_user.id)
    except invites_service.InviteNotFoundError:
        await message.answer("Приглашение не найдено. Уточните ссылку у того, кто его выдал.")
        return
    except invites_service.InviteAlreadyUsedError:
        await message.answer("Это приглашение уже использовано.")
        return
    except invites_service.AlreadyHasRoleError as exc:
        await message.answer(
            f"У вашего аккаунта уже назначена роль «{exc.existing_role.value}» — это приглашение для неё не применяется."
        )
        return

    if invite.target_role == InviteTargetRole.SUPPLIER:
        await message.answer("Вы зарегистрированы как поставщик Miramax Bonus.")
        return
    if invite.target_role == InviteTargetRole.SELLER:
        await message.answer("Вы привязаны к магазину как продавец Miramax Bonus.")
        return

    # CUSTOMER invite: the CustomerCard already existed (created by a seller) and just
    # got this telegram_id attached — this is their first time seeing this bot, so run
    # them through the same language picker as a fresh /start before greeting them.
    customer = await _get_or_create_customer(session, message)
    if customer.language is None:
        await message.answer(CHOOSE_LANGUAGE_FIRST_RUN, reply_markup=language_menu())
        return
    await _send_menu(message, session, customer)


@router.message(Command("menu"))
async def menu_command(message: Message, session: AsyncSession) -> None:
    await start_plain(message, session)


@router.message(Command("catalog"))
async def catalog_command(message: Message) -> None:
    await message.answer("Katalogni Mini App orqali oching.", reply_markup=catalog_webapp_keyboard())


@router.message(F.text.in_(BALANCE_LABELS))
@router.message(Command("balance"))
async def balance_command(message: Message, session: AsyncSession) -> None:
    customer = await _get_or_create_customer(session, message)
    balance = await _customer_balance(session, customer.id)
    lang = customer.language or DEFAULT_LANG
    await message.answer(t(lang, "balance_label", balance=_points(balance)))


@router.message(F.text.in_(PRODUCTS_LABELS))
@router.message(Command("products"))
async def products_command(message: Message, session: AsyncSession) -> None:
    await _send_product_carousel(message, session, 0)


async def _send_product_carousel(message: Message, session: AsyncSession, position: int) -> None:
    customer = await _get_or_create_customer(session, message)
    lang = customer.language or DEFAULT_LANG
    product, position, total = await _product_by_position(session, position)
    if product is None:
        await message.answer("Katalogda hozircha faol tovar yo'q.", reply_markup=catalog_webapp_keyboard())
        return

    text = _carousel_text(product, position, total)
    keyboard = _carousel_keyboard(lang, position, total, product.id)
    image_url = product.icon_or_image_url or ""
    if image_url.startswith("http"):
        try:
            await message.answer_photo(image_url, caption=text, reply_markup=keyboard)
            return
        except TelegramBadRequest:
            pass
    await message.answer(text, reply_markup=keyboard)


async def _send_products_page(message: Message, session: AsyncSession, page: int) -> None:
    products, total = await _product_page(session, page)
    if not products:
        await message.answer("Katalogda hozircha faol tovar yo'q.", reply_markup=catalog_webapp_keyboard())
        return
    page_count = max((total - 1) // PRODUCTS_PAGE_SIZE + 1, 1)
    text = (
        f"Tovarlar katalogi ({page + 1}/{page_count})\n"
        f"Har sahifada {PRODUCTS_PAGE_SIZE} ta tovar.\n\n"
        f"{_product_lines(products, start=page * PRODUCTS_PAGE_SIZE + 1)}"
    )
    await message.answer(text, reply_markup=_products_keyboard(products, page, total))


@router.callback_query(F.data.startswith("products_page:"))
async def products_page_callback(callback: CallbackQuery, session: AsyncSession) -> None:
    page = int((callback.data or "products_page:0").split(":")[1])
    products, total = await _product_page(session, page)
    page_count = max((total - 1) // PRODUCTS_PAGE_SIZE + 1, 1)
    text = (
        f"Tovarlar katalogi ({page + 1}/{page_count})\n"
        f"Har sahifada {PRODUCTS_PAGE_SIZE} ta tovar.\n\n"
        f"{_product_lines(products, start=page * PRODUCTS_PAGE_SIZE + 1)}"
    )
    await callback.message.edit_text(text, reply_markup=_products_keyboard(products, page, total))
    await callback.answer()


@router.callback_query(F.data.startswith("carousel:"))
async def carousel_callback(callback: CallbackQuery, session: AsyncSession) -> None:
    customer = await _get_or_create_customer_by_id(session, callback.from_user.id, _full_name_from_user(callback.from_user))
    lang = customer.language or DEFAULT_LANG
    position = int((callback.data or "carousel:0").split(":")[1])
    product, position, total = await _product_by_position(session, position)
    if product is None:
        await callback.answer("Katalog bo'sh.", show_alert=True)
        return

    text = _carousel_text(product, position, total)
    keyboard = _carousel_keyboard(lang, position, total, product.id)
    image_url = product.icon_or_image_url or ""
    if image_url.startswith("http"):
        try:
            if callback.message.photo:
                await callback.message.edit_media(
                    media=InputMediaPhoto(media=image_url, caption=text, parse_mode="HTML"),
                    reply_markup=keyboard,
                )
            else:
                await callback.message.answer_photo(image_url, caption=text, reply_markup=keyboard)
            await callback.answer()
            return
        except TelegramBadRequest:
            pass

    if callback.message.photo:
        await callback.message.answer(text, reply_markup=keyboard)
    else:
        await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("product:"))
async def product_detail_callback(callback: CallbackQuery, session: AsyncSession) -> None:
    customer = await _get_or_create_customer_by_id(session, callback.from_user.id, _full_name_from_user(callback.from_user))
    lang = customer.language or DEFAULT_LANG
    _, product_id_raw, page_raw = (callback.data or "product:0:0").split(":")
    product = await session.get(Product, int(product_id_raw))
    position = int(page_raw)
    if product is None or not product.active:
        await callback.answer("Tovar topilmadi.", show_alert=True)
        return

    text = _product_detail_text(product)
    keyboard = _product_detail_keyboard(lang, position, product.id)
    image_url = product.icon_or_image_url or ""
    if image_url.startswith("http"):
        try:
            await callback.message.answer_photo(image_url, caption=text, reply_markup=keyboard)
        except TelegramBadRequest:
            await callback.message.answer(text, reply_markup=keyboard)
    else:
        await callback.message.answer(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "noop")
async def noop_callback(callback: CallbackQuery) -> None:
    await callback.answer()


@router.callback_query(F.data.startswith("redeem:"))
async def redeem_callback(callback: CallbackQuery, session: AsyncSession) -> None:
    customer = await _get_or_create_customer_by_id(session, callback.from_user.id, _full_name_from_user(callback.from_user))
    lang = customer.language or DEFAULT_LANG
    _, product_id_raw, position_raw = (callback.data or "redeem:0:0").split(":")
    product = await session.get(Product, int(product_id_raw))
    if product is None or not product.active:
        await callback.answer(t(lang, "redeem_product_not_found"), show_alert=True)
        return

    try:
        redemption = await redemptions_service.create_redemption(session, customer.id, product.id, qty=1)
    except redemptions_service.InsufficientBalanceError as exc:
        await callback.answer(t(lang, "redeem_insufficient", cost=_points(exc.needed), balance=_points(exc.balance)), show_alert=True)
        return

    await callback.answer()
    await callback.message.answer(
        t(lang, "redeem_created", name=redemption.product.name, qty=redemption.qty, points=_points(redemption.points_spent))
    )


@router.message(F.text.in_(REDEEM_LABELS))
async def redeem_button(message: Message, session: AsyncSession) -> None:
    await _send_product_carousel(message, session, 0)


@router.message(F.text.in_(CALL_STORE_LABELS))
async def call_store_button(message: Message, session: AsyncSession) -> None:
    customer = await _get_or_create_customer(session, message)
    lang = customer.language or DEFAULT_LANG
    await message.answer(
        t(lang, "call_store_text", phone=settings.store_phone),
        reply_markup=call_store_keyboard(lang),
    )


@router.message(F.text.in_(INFO_LABELS))
async def info_button(message: Message, session: AsyncSession) -> None:
    customer = await _get_or_create_customer(session, message)
    lang = customer.language or DEFAULT_LANG
    await message.answer(t(lang, "info_text"))


@router.message(F.text.in_(SEARCH_LABELS))
async def search_button(message: Message, state: FSMContext) -> None:
    await state.set_state(SearchProductForm.waiting_query)
    await message.answer("Qaysi tovarni qidiramiz? Nomini yoki kategoriyasini yozing.")


@router.message(Command("search"))
async def search_command(message: Message, command: CommandObject, session: AsyncSession, state: FSMContext) -> None:
    query = (command.args or "").strip()
    if not query:
        await search_button(message, state)
        return
    await _send_search_results(message, session, query)


@router.message(SearchProductForm.waiting_query)
async def search_query(message: Message, state: FSMContext, session: AsyncSession) -> None:
    await state.clear()
    await _send_search_results(message, session, message.text or "")


async def _send_search_results(message: Message, session: AsyncSession, query: str) -> None:
    query = query.strip()
    if len(query) < 2:
        await message.answer("Qidirish uchun kamida 2 ta belgi yozing.")
        return
    pattern = f"%{query}%"
    result = await session.execute(
        select(Product)
        .where(
            Product.active.is_(True),
            or_(Product.name.ilike(pattern), Product.category.ilike(pattern)),
        )
        .order_by(Product.category, Product.name)
        .limit(20)
    )
    products = list(result.scalars().all())
    await message.answer(f"Qidiruv: <b>{query}</b>\n\n{_product_lines(products)}", reply_markup=catalog_webapp_keyboard())


@router.message(F.text.in_(HISTORY_LABELS))
@router.message(Command("history"))
async def history_command(message: Message, session: AsyncSession) -> None:
    customer = await _get_or_create_customer(session, message)
    purchases_result = await session.execute(
        select(PointsTransaction, Store)
        .outerjoin(Store, PointsTransaction.store_id == Store.id)
        .where(PointsTransaction.customer_id == customer.id)
        .order_by(PointsTransaction.created_at.desc())
        .limit(20)
    )
    purchases = list(purchases_result.all())

    redemptions_result = await session.execute(
        select(Redemption)
        .options(selectinload(Redemption.product))
        .where(Redemption.customer_id == customer.id)
        .order_by(Redemption.created_at.desc())
        .limit(20)
    )
    redemptions = list(redemptions_result.scalars().all())

    if not purchases and not redemptions:
        await message.answer("Tarix hozircha bo'sh.")
        return

    sections = []
    if purchases:
        purchase_lines = []
        for transaction, store in purchases:
            store_name = store.name if store else "Noma'lum do'kon"
            reason = transaction.reason or "Xarid"
            purchase_lines.append(
                f"• <b>{reason}</b>\n"
                f"   Do'kon: {store_name}\n"
                f"   Qo'shilgan: <b>{_points(transaction.points)} ball</b>"
            )
        sections.append("Xaridlar va ball tarixi:\n" + "\n".join(purchase_lines))

    status_labels = {
        RedemptionStatus.PENDING: "kutilmoqda",
        RedemptionStatus.FULFILLED: "berildi",
        RedemptionStatus.CANCELLED: "bekor qilindi",
    }
    if redemptions:
        redemption_lines = [
            f"• <b>{item.product.name}</b> x{item.qty} - {_points(item.points_spent)} ball ({status_labels[item.status]})"
            for item in redemptions
        ]
        sections.append("Ball almashtirish tarixi:\n" + "\n".join(redemption_lines))

    await message.answer("\n\n".join(sections))


@router.message(Command("help"))
async def help_command(message: Message, session: AsyncSession) -> None:
    customer = await _get_or_create_customer(session, message)
    lang = customer.language or DEFAULT_LANG
    await message.answer(t(lang, "info_text"), reply_markup=customer_menu(lang))
