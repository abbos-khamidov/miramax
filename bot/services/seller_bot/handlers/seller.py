import io

import qrcode
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, Message
from sqlalchemy.ext.asyncio import AsyncSession

from core.services import customers as customers_service
from core.services import invites as invites_service
from core.services import roles as roles_service
from services.seller_bot.i18n import t
from services.seller_bot.keyboards import (
    ADD_CLIENT_LABELS,
    BACK_OR_CANCEL_LABELS,
    INFO_LABELS,
    SUPPORT_LABELS,
    back_menu,
    seller_menu,
)
from services.seller_bot.states import AddClientForm

router = Router(name="seller")


async def _lang_for(session: AsyncSession, telegram_id: int) -> str:
    role = await roles_service.get_role_by_telegram_id(session, telegram_id)
    return (role.language if role else None) or "ru"


async def send_seller_menu(message: Message, lang: str) -> None:
    await message.answer(t(lang, "help_seller"), reply_markup=seller_menu(lang))


@router.message(F.text.in_(ADD_CLIENT_LABELS))
async def add_client_start(message: Message, state: FSMContext, session: AsyncSession) -> None:
    lang = await _lang_for(session, message.from_user.id)
    await state.update_data(lang=lang)
    await state.set_state(AddClientForm.waiting_first_name)
    await message.answer(t(lang, "ask_client_first_name"), reply_markup=back_menu(lang))


@router.message(AddClientForm(), F.text.in_(BACK_OR_CANCEL_LABELS))
async def add_client_cancel(message: Message, state: FSMContext, session: AsyncSession) -> None:
    lang = await _lang_for(session, message.from_user.id)
    await state.clear()
    await send_seller_menu(message, lang)


@router.message(AddClientForm.waiting_first_name)
async def add_client_first_name(message: Message, state: FSMContext) -> None:
    data = await state.update_data(first_name=message.text)
    await state.set_state(AddClientForm.waiting_last_name)
    await message.answer(t(data["lang"], "ask_client_last_name"), reply_markup=back_menu(data["lang"]))


@router.message(AddClientForm.waiting_last_name)
async def add_client_last_name(message: Message, state: FSMContext) -> None:
    data = await state.update_data(last_name=message.text)
    await state.set_state(AddClientForm.waiting_phone)
    await message.answer(t(data["lang"], "ask_client_phone"), reply_markup=back_menu(data["lang"]))


@router.message(AddClientForm.waiting_phone)
async def add_client_phone(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.update_data(phone=message.text)
    lang = data["lang"]
    await state.clear()

    full_name = " ".join(part for part in [data["first_name"], data["last_name"]] if part)
    existing = await customers_service.search_customers(session, data["phone"], limit=1)
    if existing:
        customer = existing[0]
    else:
        role = await roles_service.get_role_by_telegram_id(session, message.from_user.id)
        customer = await customers_service.create_pending_customer(
            session, first_name=full_name, phone=data["phone"], store_id=role.store_id if role else None
        )

    await message.answer(
        t(lang, "client_registered", name=customer.full_name or full_name),
        reply_markup=seller_menu(lang),
    )

    if customer.telegram_id is None:
        invite, link = await invites_service.create_customer_invite(
            session, customer_card_id=customer.id, first_name=full_name, phone=data["phone"]
        )
        qr_img = qrcode.make(link)
        buf = io.BytesIO()
        qr_img.save(buf, format="PNG")
        buf.seek(0)
        await message.answer_photo(
            BufferedInputFile(buf.read(), filename="invite.png"),
            caption=t(lang, "new_customer_invite_caption", link=link),
        )


@router.message(F.text.in_(INFO_LABELS))
async def info(message: Message, session: AsyncSession) -> None:
    lang = await _lang_for(session, message.from_user.id)
    await message.answer(t(lang, "info_text"))


@router.message(F.text.in_(SUPPORT_LABELS))
async def support(message: Message, session: AsyncSession) -> None:
    lang = await _lang_for(session, message.from_user.id)
    await message.answer(t(lang, "support_text"))
