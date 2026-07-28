import io

import qrcode
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import CustomerCard, Product
from core.services import customers as customers_service
from core.services import invites as invites_service
from core.services import redemptions as redemptions_service
from core.services import roles as roles_service
from core.services.notifications import notify_customer
from services.seller_bot.i18n import t
from services.seller_bot.keyboards import (
    ADD_CLIENT_LABELS,
    BACK_LABELS,
    BALANCE_LABELS,
    EXCHANGE_LABELS,
    INFO_LABELS,
    NOVINKI_LABELS,
    SUPPORT_LABELS,
    back_menu,
    exchange_list_menu,
    match_list_menu,
    seller_menu,
)
from services.seller_bot.states import AddClientForm, BalanceLookupForm, ExchangeForm

router = Router(name="seller")

NOVINKI_LIMIT = 8
MATCH_LIMIT = 6


def _fmt(value: float) -> str:
    return f"{value:,.0f}".replace(",", " ")


async def _lang_for(session: AsyncSession, telegram_id: int) -> str:
    role = await roles_service.get_role_by_telegram_id(session, telegram_id)
    return (role.language if role else None) or "ru"


def _match_map(lang: str, customers: list[CustomerCard]) -> tuple[list[str], dict[str, int]]:
    label_map: dict[str, int] = {}
    labels: list[str] = []
    for customer in customers:
        label = t(lang, "match_list_line", name=customer.full_name or "—", phone=customer.phone or "—")
        base_label, suffix = label, 2
        while label in label_map:
            label = f"{base_label} ({suffix})"
            suffix += 1
        label_map[label] = customer.id
        labels.append(label)
    return labels, label_map


async def send_seller_menu(message: Message, lang: str) -> None:
    await message.answer(t(lang, "help_seller"), reply_markup=seller_menu(lang))


@router.message(F.text.in_(ADD_CLIENT_LABELS))
async def add_client_start(message: Message, state: FSMContext, session: AsyncSession) -> None:
    lang = await _lang_for(session, message.from_user.id)
    await state.update_data(lang=lang)
    await state.set_state(AddClientForm.waiting_phone)
    await message.answer(t(lang, "ask_client_phone"), reply_markup=back_menu(lang))


@router.message(AddClientForm(), F.text.in_(BACK_LABELS))
async def add_client_cancel(message: Message, state: FSMContext, session: AsyncSession) -> None:
    lang = await _lang_for(session, message.from_user.id)
    await state.clear()
    await send_seller_menu(message, lang)


@router.message(AddClientForm.waiting_phone)
async def add_client_phone(message: Message, state: FSMContext) -> None:
    data = await state.update_data(phone=message.text)
    await state.set_state(AddClientForm.waiting_name)
    await message.answer(t(data["lang"], "ask_client_name"), reply_markup=back_menu(data["lang"]))


@router.message(AddClientForm.waiting_name)
async def add_client_name(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.update_data(name=message.text)
    lang = data["lang"]
    phone = data["phone"]

    matches = await customers_service.search_customers(session, phone, limit=MATCH_LIMIT)
    if len(matches) == 1:
        await state.update_data(customer_id=matches[0].id, is_new=False)
        await state.set_state(AddClientForm.waiting_amount)
        await message.answer(t(lang, "ask_client_amount"), reply_markup=back_menu(lang))
        return
    if len(matches) > 1:
        labels, match_map = _match_map(lang, matches)
        await state.update_data(match_map=match_map)
        await state.set_state(AddClientForm.choosing_match)
        await message.answer(t(lang, "match_list_header"), reply_markup=match_list_menu(lang, labels, allow_new=True))
        return

    customer = await customers_service.create_pending_customer(session, first_name=data["name"], phone=phone)
    await state.update_data(customer_id=customer.id, is_new=True)
    await state.set_state(AddClientForm.waiting_amount)
    await message.answer(t(lang, "ask_client_amount"), reply_markup=back_menu(lang))


@router.message(AddClientForm.choosing_match)
async def add_client_choose_match(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    lang = data["lang"]

    if message.text == t(lang, "match_create_new"):
        customer = await customers_service.create_pending_customer(session, first_name=data["name"], phone=data["phone"])
        await state.update_data(customer_id=customer.id, is_new=True)
    else:
        customer_id = data.get("match_map", {}).get(message.text)
        if customer_id is None:
            return
        await state.update_data(customer_id=customer_id, is_new=False)

    await state.set_state(AddClientForm.waiting_amount)
    await message.answer(t(lang, "ask_client_amount"), reply_markup=back_menu(lang))


@router.message(AddClientForm.waiting_amount)
async def add_client_amount(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    lang = data["lang"]
    await state.clear()

    try:
        amount = float((message.text or "").replace(",", ".").strip())
    except ValueError:
        await message.answer(t(lang, "amount_invalid"))
        return

    role = await roles_service.get_role_by_telegram_id(session, message.from_user.id)
    if role is None or role.store_id is None:
        await message.answer(t(lang, "no_store_link"))
        return

    transaction = await customers_service.record_sale(
        session,
        customer_id=data["customer_id"],
        store_id=role.store_id,
        seller_telegram_id=message.from_user.id,
        amount=amount,
        product_name="Покупка",
    )

    customer = await customers_service.get_customer(session, data["customer_id"])
    client_name = customer.full_name if customer else data["name"]

    await message.answer(
        t(lang, "client_points_added", points=transaction.points, name=client_name, amount=_fmt(amount)),
        reply_markup=seller_menu(lang),
    )

    if customer is not None and customer.telegram_id is not None:
        balance = await customers_service.get_customer_balance(session, customer.id)
        await notify_customer(
            customer.telegram_id,
            f"🎉 Вам начислено <b>{transaction.points} баллов</b> за покупку на {_fmt(amount)}.\n"
            f"Ваш баланс: <b>{_fmt(balance)} баллов</b>.",
        )

    if data.get("is_new"):
        invite, link = await invites_service.create_customer_invite(
            session, customer_card_id=data["customer_id"], first_name=client_name, phone=data.get("phone", "")
        )
        qr_img = qrcode.make(link)
        buf = io.BytesIO()
        qr_img.save(buf, format="PNG")
        buf.seek(0)
        await message.answer_photo(
            BufferedInputFile(buf.read(), filename="invite.png"),
            caption=t(lang, "new_customer_invite_caption", link=link),
        )


@router.message(F.text.in_(NOVINKI_LABELS))
async def novinki(message: Message, session: AsyncSession) -> None:
    lang = await _lang_for(session, message.from_user.id)
    result = await session.execute(
        select(Product).where(Product.active.is_(True)).order_by(Product.created_at.desc()).limit(NOVINKI_LIMIT)
    )
    products = list(result.scalars().all())
    if not products:
        await message.answer(t(lang, "novinki_empty"))
        return

    lines = [t(lang, "novinki_line", name=p.name, category=p.category, points_cost=p.points_cost) for p in products]
    await message.answer(t(lang, "novinki_header") + "\n" + "\n".join(lines))


@router.message(F.text.in_(BALANCE_LABELS))
async def balance_lookup_start(message: Message, state: FSMContext, session: AsyncSession) -> None:
    lang = await _lang_for(session, message.from_user.id)
    await state.update_data(lang=lang)
    await state.set_state(BalanceLookupForm.waiting_query)
    await message.answer(t(lang, "ask_lookup_phone"), reply_markup=back_menu(lang))


@router.message(BalanceLookupForm(), F.text.in_(BACK_LABELS))
async def balance_lookup_cancel(message: Message, state: FSMContext, session: AsyncSession) -> None:
    lang = await _lang_for(session, message.from_user.id)
    await state.clear()
    await send_seller_menu(message, lang)


async def _send_balance(message: Message, session: AsyncSession, lang: str, customer: CustomerCard) -> None:
    balance = await customers_service.get_customer_balance(session, customer.id)
    await message.answer(
        t(lang, "balance_result", name=customer.full_name or "—", phone=customer.phone or "—", balance=_fmt(balance)),
        reply_markup=seller_menu(lang),
    )


@router.message(BalanceLookupForm.waiting_query)
async def balance_lookup_result(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    lang = data["lang"]

    matches = await customers_service.search_customers(session, message.text or "", limit=MATCH_LIMIT)
    if not matches:
        await state.clear()
        await message.answer(t(lang, "lookup_not_found"), reply_markup=seller_menu(lang))
        return
    if len(matches) == 1:
        await state.clear()
        await _send_balance(message, session, lang, matches[0])
        return

    labels, match_map = _match_map(lang, matches)
    await state.update_data(match_map=match_map)
    await state.set_state(BalanceLookupForm.choosing_match)
    await message.answer(t(lang, "match_list_header"), reply_markup=match_list_menu(lang, labels, allow_new=False))


@router.message(BalanceLookupForm.choosing_match)
async def balance_lookup_choose_match(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    lang = data["lang"]
    customer_id = data.get("match_map", {}).get(message.text)
    if customer_id is None:
        return

    await state.clear()
    customer = await customers_service.get_customer(session, customer_id)
    if customer is None:
        await message.answer(t(lang, "lookup_not_found"), reply_markup=seller_menu(lang))
        return
    await _send_balance(message, session, lang, customer)


@router.message(F.text.in_(EXCHANGE_LABELS))
async def exchange_start(message: Message, state: FSMContext, session: AsyncSession) -> None:
    lang = await _lang_for(session, message.from_user.id)
    await state.update_data(lang=lang)
    await state.set_state(ExchangeForm.waiting_query)
    await message.answer(t(lang, "ask_lookup_phone"), reply_markup=back_menu(lang))


@router.message(ExchangeForm(), F.text.in_(BACK_LABELS))
async def exchange_cancel(message: Message, state: FSMContext, session: AsyncSession) -> None:
    lang = await _lang_for(session, message.from_user.id)
    await state.clear()
    await send_seller_menu(message, lang)


async def _show_pending(message: Message, state: FSMContext, session: AsyncSession, lang: str, customer: CustomerCard) -> None:
    pending = await redemptions_service.list_pending_for_customer(session, customer.id)
    if not pending:
        await state.clear()
        await message.answer(t(lang, "exchange_none_pending"), reply_markup=seller_menu(lang))
        return

    label_map: dict[str, int] = {}
    labels: list[str] = []
    for redemption in pending:
        label = t(lang, "exchange_item_button", product_name=redemption.product.name, qty=redemption.qty, points=redemption.points_spent)
        base_label, suffix = label, 2
        while label in label_map:
            label = f"{base_label} ({suffix})"
            suffix += 1
        label_map[label] = redemption.id
        labels.append(label)

    await state.set_state(ExchangeForm.listing)
    await state.update_data(redemption_map=label_map)
    await message.answer(
        t(lang, "exchange_list_header", name=customer.full_name or "—"),
        reply_markup=exchange_list_menu(lang, labels),
    )


@router.message(ExchangeForm.waiting_query)
async def exchange_query(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    lang = data["lang"]

    matches = await customers_service.search_customers(session, message.text or "", limit=MATCH_LIMIT)
    if not matches:
        await message.answer(t(lang, "lookup_not_found"))
        return
    if len(matches) == 1:
        await _show_pending(message, state, session, lang, matches[0])
        return

    labels, match_map = _match_map(lang, matches)
    await state.update_data(match_map=match_map)
    await state.set_state(ExchangeForm.choosing_match)
    await message.answer(t(lang, "match_list_header"), reply_markup=match_list_menu(lang, labels, allow_new=False))


@router.message(ExchangeForm.choosing_match)
async def exchange_choose_match(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    lang = data["lang"]
    customer_id = data.get("match_map", {}).get(message.text)
    if customer_id is None:
        return

    customer = await customers_service.get_customer(session, customer_id)
    if customer is None:
        await state.clear()
        await message.answer(t(lang, "lookup_not_found"), reply_markup=seller_menu(lang))
        return
    await _show_pending(message, state, session, lang, customer)


@router.message(ExchangeForm.listing)
async def exchange_confirm(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    lang = data["lang"]
    redemption_id = data.get("redemption_map", {}).get(message.text)
    if redemption_id is None:
        return

    try:
        redemption = await redemptions_service.fulfill_redemption(session, redemption_id, message.from_user.id)
    except redemptions_service.RedemptionNotPendingError:
        await message.answer(t(lang, "exchange_already_done"))
        return
    except redemptions_service.InsufficientBalanceError as exc:
        await message.answer(t(lang, "exchange_insufficient_balance", needed=exc.needed, balance=exc.balance))
        return

    await state.clear()
    await message.answer(
        t(lang, "exchange_confirmed", product_name=redemption.product.name, qty=redemption.qty, points=redemption.points_spent),
        reply_markup=seller_menu(lang),
    )

    customer = await customers_service.get_customer(session, redemption.customer_id)
    if customer is not None and customer.telegram_id is not None:
        customer_lang = customer.language or "ru"
        await notify_customer(
            customer.telegram_id,
            t(customer_lang, "exchange_customer_notify", product_name=redemption.product.name, qty=redemption.qty),
        )


@router.message(F.text.in_(INFO_LABELS))
async def info(message: Message, session: AsyncSession) -> None:
    lang = await _lang_for(session, message.from_user.id)
    await message.answer(t(lang, "info_text"))


@router.message(F.text.in_(SUPPORT_LABELS))
async def support(message: Message, session: AsyncSession) -> None:
    lang = await _lang_for(session, message.from_user.id)
    await message.answer(t(lang, "support_text"))
