import io

import qrcode
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import CustomerCard
from core.services import customers as customers_service
from core.services import invites as invites_service
from core.services import roles as roles_service
from core.services import tiers as tiers_service
from core.services.notifications import notify_customer
from services.seller_bot.i18n import t
from services.seller_bot.keyboards import (
    BACK_OR_CANCEL_LABELS,
    ISSUE_POINTS_LABELS,
    back_menu,
    confirm_new_client_keyboard,
    match_list_menu,
    seller_menu,
    tier_composer_keyboard,
)
from services.seller_bot.states import IssuePointsForm

router = Router(name="issue_points")

MATCH_LIMIT = 6

# Guards against a fast double-tap firing the same write twice (duplicate customer,
# double-awarded points) — Telegram delivers each tap as its own callback_query, and
# aiogram processes updates concurrently, so nothing else serializes these. Checked
# and set synchronously (no `await` in between), so it's race-free within one process.
_in_flight_sellers: set[int] = set()


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


@router.message(F.text.in_(ISSUE_POINTS_LABELS))
async def issue_points_start(message: Message, state: FSMContext, session: AsyncSession) -> None:
    lang = await _lang_for(session, message.from_user.id)
    await state.update_data(lang=lang)
    await state.set_state(IssuePointsForm.waiting_phone)
    await message.answer(t(lang, "ask_client_phone"), reply_markup=back_menu(lang))


@router.message(IssuePointsForm(), F.text.in_(BACK_OR_CANCEL_LABELS))
async def issue_points_cancel(message: Message, state: FSMContext, session: AsyncSession) -> None:
    lang = await _lang_for(session, message.from_user.id)
    await state.clear()
    await message.answer(t(lang, "help_seller"), reply_markup=seller_menu(lang))


def _compose_text(lang: str, cart: dict[int, int]) -> str:
    lines = [t(lang, "tier_compose_header")]
    if cart:
        lines.append("")
        total_amount = 0
        for tier in sorted(cart):
            qty = cart[tier]
            total_amount += tier * qty
            lines.append(t(lang, "tier_compose_line", tier=f"{tier:,}".replace(",", " "), qty=qty))
        lines.append("")
        lines.append(t(lang, "tier_compose_total", amount=f"{total_amount:,}".replace(",", " ")))
    return "\n".join(lines)


async def _start_composing(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    lang = data["lang"]
    tiers = await tiers_service.load_tiers(session)
    await state.update_data(cart={})
    await state.set_state(IssuePointsForm.composing)
    await message.answer(
        _compose_text(lang, {}), reply_markup=tier_composer_keyboard(lang, list(tiers), {}, total_points=0)
    )


@router.message(IssuePointsForm.waiting_phone)
async def issue_points_phone(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.update_data(phone=message.text)
    lang = data["lang"]

    matches = await customers_service.search_customers(session, message.text or "", limit=MATCH_LIMIT)
    if len(matches) == 1:
        customer = matches[0]
        await state.update_data(customer_id=customer.id, is_new=False)
        await message.answer(t(lang, "client_found", name=customer.full_name or "—", phone=customer.phone or "—"))
        await _start_composing(message, state, session)
        return
    if len(matches) > 1:
        labels, match_map = _match_map(lang, matches)
        await state.update_data(match_map=match_map)
        await state.set_state(IssuePointsForm.choosing_match)
        await message.answer(t(lang, "match_list_header"), reply_markup=match_list_menu(lang, labels, allow_new=True))
        return

    await state.set_state(IssuePointsForm.confirming_new)
    await message.answer(t(lang, "client_not_found_confirm"), reply_markup=confirm_new_client_keyboard(lang))


@router.callback_query(IssuePointsForm.confirming_new, F.data == "new_client_yes")
async def confirm_new_client_yes(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    lang = data["lang"]
    await state.set_state(IssuePointsForm.waiting_new_first_name)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer()
    await callback.message.answer(t(lang, "ask_client_first_name"), reply_markup=back_menu(lang))


@router.callback_query(IssuePointsForm.confirming_new, F.data == "new_client_no")
async def confirm_new_client_no(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    lang = data["lang"]
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer()
    await callback.message.answer(t(lang, "help_seller"), reply_markup=seller_menu(lang))


@router.message(IssuePointsForm.waiting_new_first_name)
async def issue_points_new_first_name(message: Message, state: FSMContext) -> None:
    data = await state.update_data(first_name=message.text)
    await state.set_state(IssuePointsForm.waiting_new_last_name)
    await message.answer(t(data["lang"], "ask_client_last_name"), reply_markup=back_menu(data["lang"]))


@router.message(IssuePointsForm.waiting_new_last_name)
async def issue_points_new_last_name(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.update_data(last_name=message.text)
    lang = data["lang"]
    full_name = " ".join(part for part in [data.get("first_name"), data.get("last_name")] if part)
    role = await roles_service.get_role_by_telegram_id(session, message.from_user.id)
    customer = await customers_service.create_pending_customer(
        session, first_name=full_name, phone=data["phone"], store_id=role.store_id if role else None
    )
    await state.update_data(customer_id=customer.id, is_new=True)
    await _start_composing(message, state, session)


@router.message(IssuePointsForm.choosing_match)
async def issue_points_choose_match(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    lang = data["lang"]

    if message.text == t(lang, "match_create_new"):
        await state.set_state(IssuePointsForm.waiting_new_first_name)
        await message.answer(t(lang, "ask_client_first_name"), reply_markup=back_menu(lang))
        return

    customer_id = data.get("match_map", {}).get(message.text)
    if customer_id is None:
        return
    await state.update_data(customer_id=customer_id, is_new=False)
    await _start_composing(message, state, session)


@router.callback_query(IssuePointsForm.composing, F.data.startswith("tier:"))
async def tier_tap(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    lang = data["lang"]
    tier = int((callback.data or "tier:0").split(":")[1])
    cart = dict(data.get("cart", {}))
    cart[tier] = cart.get(tier, 0) + 1
    await state.update_data(cart=cart)

    tiers = await tiers_service.load_tiers(session)
    total_points = await tiers_service.points_for_cart(session, cart)
    await callback.message.edit_text(
        _compose_text(lang, cart), reply_markup=tier_composer_keyboard(lang, list(tiers), cart, total_points)
    )
    await callback.answer()


@router.callback_query(IssuePointsForm.composing, F.data == "tier_reset")
async def tier_reset(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    lang = data["lang"]
    await state.update_data(cart={})

    tiers = await tiers_service.load_tiers(session)
    await callback.message.edit_text(
        _compose_text(lang, {}), reply_markup=tier_composer_keyboard(lang, list(tiers), {}, total_points=0)
    )
    await callback.answer()


@router.callback_query(IssuePointsForm.composing, F.data == "tier_confirm")
async def tier_confirm(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    seller_id = callback.from_user.id
    if seller_id in _in_flight_sellers:
        await callback.answer()
        return
    _in_flight_sellers.add(seller_id)
    try:
        data = await state.get_data()
        lang = data["lang"]
        cart: dict[int, int] = data.get("cart", {})

        total_points = await tiers_service.points_for_cart(session, cart)
        if total_points <= 0:
            await callback.answer(t(lang, "tier_amount_too_small"), show_alert=True)
            return

        role = await roles_service.get_role_by_telegram_id(session, callback.from_user.id)
        if role is None or role.store_id is None:
            await callback.answer(t(lang, "no_store_link"), show_alert=True)
            return

        _sale_id, total_points = await tiers_service.record_tier_sale(
            session,
            customer_id=data["customer_id"],
            store_id=role.store_id,
            seller_telegram_id=callback.from_user.id,
            cart=cart,
        )
        await state.clear()

        customer = await customers_service.get_customer(session, data["customer_id"])
        full_name = " ".join(part for part in [data.get("first_name"), data.get("last_name")] if part)
        client_name = customer.full_name if customer else full_name

        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.answer()
        await callback.message.answer(
            t(lang, "tier_sale_confirmed", points=f"{total_points:,}".replace(",", " "), name=client_name),
            reply_markup=seller_menu(lang),
        )

        if customer is not None and customer.telegram_id is not None:
            balance = await customers_service.get_customer_balance(session, customer.id)
            await notify_customer(
                customer.telegram_id,
                f"🎉 Вам начислено <b>{total_points} баллов</b>.\n"
                f"Ваш баланс: <b>{balance} баллов</b>.",
            )

        if data.get("is_new"):
            invite, link = await invites_service.create_customer_invite(
                session, customer_card_id=data["customer_id"], first_name=client_name, phone=data.get("phone", "")
            )
            qr_img = qrcode.make(link)
            buf = io.BytesIO()
            qr_img.save(buf, format="PNG")
            buf.seek(0)
            await callback.message.answer_photo(
                BufferedInputFile(buf.read(), filename="invite.png"),
                caption=t(lang, "new_customer_invite_caption", link=link),
            )
    finally:
        _in_flight_sellers.discard(seller_id)
