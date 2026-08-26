from aiogram import F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message, User
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.models import CustomerCard, InviteTargetRole, PointsTransaction, Product, Redemption, RedemptionStatus, Store
from core.services import invites as invites_service
from core.services.link_auth import issue_link_token
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
    PRIZES_LABELS,
    call_store_keyboard,
    catalog_link_keyboard,
    customer_menu,
    language_menu,
)

router = Router(name="client")


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


async def _prize_progress(session: AsyncSession, balance: int) -> tuple[Product | None, Product | None]:
    """(highest prize the balance already covers, cheapest prize still out of reach) —
    prizes ordered by points_cost, so one linear pass finds both."""
    result = await session.execute(select(Product).where(Product.active.is_(True)).order_by(Product.points_cost))
    current: Product | None = None
    next_prize: Product | None = None
    for prize in result.scalars().all():
        if prize.points_cost <= balance:
            current = prize
        elif next_prize is None:
            next_prize = prize
    return current, next_prize


def _points(value: int) -> str:
    return f"{value:,}".replace(",", " ")


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


def _catalog_url(telegram_id: int) -> str:
    token = issue_link_token(telegram_id)
    return f"{settings.miniapp_url}?tab=catalog&token={token}"


@router.message(F.text.in_(PRIZES_LABELS))
@router.message(Command("catalog"))
async def catalog_command(message: Message, session: AsyncSession) -> None:
    customer = await _get_or_create_customer(session, message)
    lang = customer.language or DEFAULT_LANG
    await message.answer(
        t(lang, "open_catalog_text"),
        reply_markup=catalog_link_keyboard(lang, _catalog_url(message.from_user.id)),
    )


@router.message(F.text.in_(BALANCE_LABELS))
@router.message(Command("balance"))
async def balance_command(message: Message, session: AsyncSession) -> None:
    customer = await _get_or_create_customer(session, message)
    balance = await _customer_balance(session, customer.id)
    lang = customer.language or DEFAULT_LANG

    lines = [t(lang, "balance_label", balance=_points(balance)), "", t(lang, "balance_redeem_instructions")]

    current, next_prize = await _prize_progress(session, balance)
    if current is not None:
        lines.append("")
        lines.append(t(lang, "balance_current_prize", name=current.name, points=_points(current.points_cost)))
    if next_prize is not None:
        needed = next_prize.points_cost - balance
        lines.append(
            t(lang, "balance_next_prize", name=next_prize.name, points=_points(next_prize.points_cost), needed=_points(needed))
        )
    elif current is not None:
        lines.append(t(lang, "balance_max_prize"))

    await message.answer("\n".join(lines))


@router.message(F.text.in_(CALL_STORE_LABELS))
async def call_store_button(message: Message, session: AsyncSession) -> None:
    customer = await _get_or_create_customer(session, message)
    lang = customer.language or DEFAULT_LANG

    store = await session.get(Store, customer.store_id) if customer.store_id else None
    phone = (store.phone if store else None) or settings.store_phone
    text_key = "call_store_text_named" if store else "call_store_text"
    text_kwargs = {"phone": phone, "store_name": store.name} if store else {"phone": phone}

    await message.answer(
        t(lang, text_key, **text_kwargs),
        reply_markup=call_store_keyboard(lang, phone),
    )


@router.message(F.text.in_(INFO_LABELS))
async def info_button(message: Message, session: AsyncSession) -> None:
    customer = await _get_or_create_customer(session, message)
    lang = customer.language or DEFAULT_LANG
    await message.answer(t(lang, "info_text"))


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
