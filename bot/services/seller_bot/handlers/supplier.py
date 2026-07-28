import io

import qrcode
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, Message
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import RoleName
from core.services import invites as invites_service
from core.services import roles as roles_service
from core.services import stores as stores_service
from core.services.analytics import get_supplier_analytics
from services.seller_bot.handlers.seller import send_seller_menu
from services.seller_bot.i18n import t
from services.seller_bot.keyboards import (
    ADD_STORE_LABELS,
    ANALYTICS_LABELS,
    BACK_LABELS,
    MY_STORES_LABELS,
    back_menu,
    seller_menu,
    supplier_menu,
)
from services.seller_bot.states import AddStoreForm

router = Router(name="supplier")


async def send_supplier_menu(message: Message, lang: str) -> None:
    await message.answer(t(lang, "help_supplier"), reply_markup=supplier_menu(lang))


async def _current_supplier_id(session: AsyncSession, telegram_id: int) -> int | None:
    """Resolves the supplier_id to add a store under, for whoever pressed the button —
    a supplier owns it directly, a seller adds under the supplier of the store they're bound to."""
    role = await roles_service.get_role_by_telegram_id(session, telegram_id)
    if role is None:
        return None
    if role.role == RoleName.SUPPLIER:
        return role.supplier_id
    if role.role == RoleName.SELLER and role.store_id is not None:
        store = await stores_service.get_store(session, role.store_id)
        return store.supplier_id if store else None
    return None


async def _menu_for_role(session: AsyncSession, telegram_id: int, lang: str):
    role = await roles_service.get_role_by_telegram_id(session, telegram_id)
    if role is not None and role.role == RoleName.SELLER:
        return seller_menu(lang)
    return supplier_menu(lang)


@router.message(F.text.in_(MY_STORES_LABELS))
async def my_stores(message: Message, session: AsyncSession) -> None:
    role = await roles_service.get_role_by_telegram_id(session, message.from_user.id)
    lang = (role.language if role else None) or "ru"
    supplier_id = role.supplier_id if role and role.role == RoleName.SUPPLIER else None
    if supplier_id is None:
        await message.answer(t(lang, "no_supplier_link"))
        return

    stores = await stores_service.list_stores_by_supplier(session, supplier_id)
    if not stores:
        await message.answer(t(lang, "my_stores_empty"))
        return

    lines = [t(lang, "my_stores_line", name=s.name, city=s.city or "—") for s in stores]
    await message.answer(t(lang, "my_stores_header") + "\n" + "\n".join(lines))


@router.message(F.text.in_(ADD_STORE_LABELS))
async def add_store_start(message: Message, state: FSMContext, session: AsyncSession) -> None:
    role = await roles_service.get_role_by_telegram_id(session, message.from_user.id)
    lang = (role.language if role else None) or "ru"
    await state.update_data(lang=lang)
    await state.set_state(AddStoreForm.waiting_first_name)
    await message.answer(t(lang, "ask_seller_first_name"), reply_markup=back_menu(lang))


@router.message(AddStoreForm(), F.text.in_(BACK_LABELS))
async def add_store_cancel(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    lang = data.get("lang", "ru")
    await state.clear()
    role = await roles_service.get_role_by_telegram_id(session, message.from_user.id)
    if role is not None and role.role == RoleName.SELLER:
        await send_seller_menu(message, lang)
    else:
        await send_supplier_menu(message, lang)


@router.message(AddStoreForm.waiting_first_name)
async def add_store_first_name(message: Message, state: FSMContext) -> None:
    data = await state.update_data(first_name=message.text)
    await state.set_state(AddStoreForm.waiting_last_name)
    await message.answer(t(data["lang"], "ask_seller_last_name"), reply_markup=back_menu(data["lang"]))


@router.message(AddStoreForm.waiting_last_name)
async def add_store_last_name(message: Message, state: FSMContext) -> None:
    data = await state.update_data(last_name=message.text)
    await state.set_state(AddStoreForm.waiting_city)
    await message.answer(t(data["lang"], "ask_city"), reply_markup=back_menu(data["lang"]))


@router.message(AddStoreForm.waiting_city)
async def add_store_city(message: Message, state: FSMContext) -> None:
    data = await state.update_data(city=message.text)
    await state.set_state(AddStoreForm.waiting_store_name)
    await message.answer(t(data["lang"], "ask_store_name"), reply_markup=back_menu(data["lang"]))


@router.message(AddStoreForm.waiting_store_name)
async def add_store_name(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.update_data(store_name=message.text)
    await state.clear()
    lang = data["lang"]

    supplier_id = await _current_supplier_id(session, message.from_user.id)
    if supplier_id is None:
        await message.answer(t(lang, "no_supplier_link"))
        return

    store = await stores_service.create_store(session, supplier_id, data["store_name"], None, data["city"])
    invite, link = await invites_service.create_seller_invite(
        session, store.id, first_name=data["first_name"], last_name=data["last_name"]
    )

    qr_img = qrcode.make(link)
    buf = io.BytesIO()
    qr_img.save(buf, format="PNG")
    buf.seek(0)

    menu = await _menu_for_role(session, message.from_user.id, lang)
    await message.answer_photo(
        BufferedInputFile(buf.read(), filename="invite.png"),
        caption=t(
            lang,
            "store_created",
            store_name=store.name,
            city=store.city,
            first_name=data["first_name"],
            last_name=data["last_name"],
            link=link,
        ),
        reply_markup=menu,
    )


@router.message(F.text.in_(ANALYTICS_LABELS))
async def supplier_analytics(message: Message, session: AsyncSession) -> None:
    role = await roles_service.get_role_by_telegram_id(session, message.from_user.id)
    lang = (role.language if role else None) or "ru"
    supplier_id = role.supplier_id if role and role.role == RoleName.SUPPLIER else None
    if supplier_id is None:
        await message.answer(t(lang, "no_supplier_link"))
        return

    analytics = await get_supplier_analytics(session, supplier_id)
    if analytics is None or not analytics.stores:
        await message.answer(t(lang, "analytics_empty"))
        return

    lines = [
        t(lang, "analytics_line", store_name=s.store_name, total_sales=s.total_sales, total_points_issued=s.total_points_issued)
        for s in analytics.stores
    ]
    await message.answer(
        t(lang, "analytics_header", supplier_name=analytics.supplier_name, store_count=analytics.store_count)
        + "\n"
        + "\n".join(lines)
    )
