import io

import qrcode
from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, Message
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.models import Product, RoleName, SupplierKind
from core.services import customers as customers_service
from core.services import directory as directory_service
from core.services import invites as invites_service
from core.services import roles as roles_service
from core.services import stores as stores_service
from core.services import tiers as tiers_service
from core.services.link_auth import issue_link_token
from core.services.analytics import get_factory_analytics, get_supplier_purchase_stats
from services.admin_bot.i18n import (
    CHOOSE_LANGUAGE_FIRST_RUN,
    FIRST_RUN_INSTRUCTION,
    LANGUAGE_CODE_BY_LABEL,
    LANGUAGE_LABELS,
    t,
)
from services.admin_bot.keyboards import (
    ADD_USER_LABELS,
    ADMIN_LABELS,
    ANALYTICS_LABELS,
    BACK_LABELS,
    LANGUAGE_MENU_LABELS,
    ONLINE_SHOWCASE_LABELS,
    POINTS_RATE_LABELS,
    VIEW_ADMIN_LABELS,
    VIEW_SEARCH_LABELS,
    VIEW_SUPPLIER_LABELS,
    VIEW_USERS_LABELS,
    VIEW_WHOLESALER_LABELS,
    WHOLESALER_LABELS,
    add_user_menu,
    entity_list_menu,
    factory_menu,
    language_menu,
    view_users_menu,
)
from services.admin_bot.states import AddProductForm, AddUserForm, PointsRateForm, ViewUsersForm

router = Router(name="admin")

_TARGET_ROLE_LABEL_KEY = {
    "admin": "submenu_admin",
    "wholesaler": "submenu_wholesaler",
}
_TARGET_KIND = {
    "wholesaler": SupplierKind.WHOLESALER,
}


async def _has_factory_access(session: AsyncSession, telegram_id: int) -> bool:
    role = await roles_service.get_role_by_telegram_id(session, telegram_id)
    return role is not None and role.role in {RoleName.FACTORY, RoleName.ADMIN}


async def _lang_for(session: AsyncSession, telegram_id: int) -> str | None:
    role = await roles_service.get_role_by_telegram_id(session, telegram_id)
    return role.language if role else None


async def send_factory_menu(message: Message, lang: str) -> None:
    await message.answer(t(lang, "welcome_instruction"), reply_markup=factory_menu(lang))


@router.message(CommandStart(deep_link=True))
async def start_with_payload(message: Message, command: CommandObject, session: AsyncSession) -> None:
    payload = command.args or ""
    if not payload.startswith("inv_"):
        await start_plain(message, session)
        return

    lang = await _lang_for(session, message.from_user.id) or "ru"
    try:
        await invites_service.redeem_invite(session, payload, message.from_user.id)
    except invites_service.InviteNotFoundError:
        await message.answer(t(lang, "invite_not_found"))
        return
    except invites_service.InviteAlreadyUsedError:
        await message.answer(t(lang, "invite_already_used"))
        return
    except invites_service.AlreadyHasRoleError as exc:
        await message.answer(t(lang, "invite_wrong_role", role=exc.existing_role.value))
        return

    await message.answer(t(lang, "admin_redeemed"))
    await start_plain(message, session)


@router.message(CommandStart())
async def start_plain(message: Message, session: AsyncSession) -> None:
    if not await _has_factory_access(session, message.from_user.id):
        await message.answer(t("ru", "no_access"))
        return

    lang = await _lang_for(session, message.from_user.id)
    if lang is None:
        await message.answer(FIRST_RUN_INSTRUCTION)
        await message.answer(CHOOSE_LANGUAGE_FIRST_RUN, reply_markup=language_menu())
        return

    await send_factory_menu(message, lang)


@router.message(Command("help"))
async def help_cmd(message: Message, session: AsyncSession) -> None:
    if not await _has_factory_access(session, message.from_user.id):
        await message.answer(t("ru", "no_access"))
        return
    lang = await _lang_for(session, message.from_user.id) or "ru"
    await message.answer(t(lang, "welcome_instruction"))


@router.message(F.text.in_(LANGUAGE_LABELS.values()))
async def language_chosen(message: Message, session: AsyncSession) -> None:
    if not await _has_factory_access(session, message.from_user.id):
        await message.answer(t("ru", "no_access"))
        return
    lang = LANGUAGE_CODE_BY_LABEL[message.text]
    await roles_service.set_language(session, message.from_user.id, lang)
    await message.answer(t(lang, "language_saved"))
    await send_factory_menu(message, lang)


@router.message(F.text.in_(LANGUAGE_MENU_LABELS))
async def language_menu_button(message: Message, session: AsyncSession) -> None:
    if not await _has_factory_access(session, message.from_user.id):
        await message.answer(t("ru", "no_access"))
        return
    lang = await _lang_for(session, message.from_user.id) or "ru"
    await message.answer(t(lang, "choose_language"), reply_markup=language_menu())


@router.message(F.text.in_(ADD_USER_LABELS))
async def add_user_menu_button(message: Message, session: AsyncSession) -> None:
    if not await _has_factory_access(session, message.from_user.id):
        await message.answer(t("ru", "no_access"))
        return
    lang = await _lang_for(session, message.from_user.id) or "ru"
    await message.answer(t(lang, "choose_user_type"), reply_markup=add_user_menu(lang))


@router.message(F.text.in_(BACK_LABELS))
async def back_to_main_menu(message: Message, state: FSMContext, session: AsyncSession) -> None:
    if not await _has_factory_access(session, message.from_user.id):
        await state.clear()
        await message.answer(t("ru", "no_access"))
        return
    lang = await _lang_for(session, message.from_user.id) or "ru"

    current_state = await state.get_state()
    if current_state == ViewUsersForm.waiting_search_phone.state:
        data = await state.get_data()
        kind = data.get("kind", "supplier")
        entities = await _list_for_kind(session, kind)
        await _render_entity_list(message, state, lang, kind, entities)
        return
    if current_state == ViewUsersForm.listing.state:
        await state.clear()
        await message.answer(t(lang, "choose_view_type"), reply_markup=view_users_menu(lang))
        return

    await state.clear()
    await send_factory_menu(message, lang)


async def _start_add_user_flow(message: Message, state: FSMContext, session: AsyncSession, target: str) -> None:
    if not await _has_factory_access(session, message.from_user.id):
        await message.answer(t("ru", "no_access"))
        return
    lang = await _lang_for(session, message.from_user.id) or "ru"
    await state.update_data(target=target, lang=lang)
    await state.set_state(AddUserForm.waiting_first_name)
    await message.answer(t(lang, "ask_first_name"))


@router.message(F.text.in_(ADMIN_LABELS))
async def add_admin_start(message: Message, state: FSMContext, session: AsyncSession) -> None:
    await _start_add_user_flow(message, state, session, "admin")


@router.message(F.text.in_(WHOLESALER_LABELS))
async def add_wholesaler_start(message: Message, state: FSMContext, session: AsyncSession) -> None:
    await _start_add_user_flow(message, state, session, "wholesaler")


@router.message(AddUserForm.waiting_first_name)
async def add_user_first_name(message: Message, state: FSMContext) -> None:
    data = await state.update_data(first_name=message.text)
    await state.set_state(AddUserForm.waiting_last_name)
    await message.answer(t(data["lang"], "ask_last_name"))


@router.message(AddUserForm.waiting_last_name)
async def add_user_last_name(message: Message, state: FSMContext) -> None:
    data = await state.update_data(last_name=message.text)
    await state.set_state(AddUserForm.waiting_phone)
    await message.answer(t(data["lang"], "ask_phone"))


@router.message(AddUserForm.waiting_phone)
async def add_user_phone(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.update_data(phone=message.text)
    lang = data["lang"]

    if data["target"] == "admin":
        if not await _has_factory_access(session, message.from_user.id):
            await state.clear()
            await message.answer(t(lang, "no_permission"))
            return
        await state.clear()

        invite, link = await invites_service.create_admin_invite(
            session, first_name=data["first_name"], last_name=data["last_name"], phone=data["phone"]
        )

        qr_img = qrcode.make(link)
        buf = io.BytesIO()
        qr_img.save(buf, format="PNG")
        buf.seek(0)

        await message.answer_photo(
            BufferedInputFile(buf.read(), filename="invite.png"),
            caption=t(
                lang,
                "admin_created",
                first_name=data["first_name"],
                last_name=data["last_name"],
                phone=data["phone"],
                link=link,
            ),
            reply_markup=factory_menu(lang),
        )
        return

    await state.set_state(AddUserForm.waiting_company_name)
    await message.answer(t(lang, "ask_company_name"))


@router.message(AddUserForm.waiting_company_name)
async def add_user_company_name(message: Message, state: FSMContext) -> None:
    data = await state.update_data(company_name=message.text)
    await state.set_state(AddUserForm.waiting_city)
    await message.answer(t(data["lang"], "ask_city"))


@router.message(AddUserForm.waiting_city)
async def add_user_city(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.update_data(city=message.text)
    lang = data["lang"]
    await state.clear()

    if not await _has_factory_access(session, message.from_user.id):
        await message.answer(t(lang, "no_permission"))
        return

    kind = _TARGET_KIND[data["target"]]
    invite, link = await invites_service.create_supplier_invite(
        session,
        company_name=data["company_name"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        phone=data["phone"],
        city=data["city"],
        kind=kind,
    )

    qr_img = qrcode.make(link)
    buf = io.BytesIO()
    qr_img.save(buf, format="PNG")
    buf.seek(0)

    await message.answer_photo(
        BufferedInputFile(buf.read(), filename="invite.png"),
        caption=t(
            lang,
            "supplier_created",
            kind_label=t(lang, "kind_wholesaler"),
            company_name=data["company_name"],
            city=data["city"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            phone=data["phone"],
            link=link,
        ),
        reply_markup=factory_menu(lang),
    )


@router.message(F.text.in_(ANALYTICS_LABELS))
async def factory_analytics(message: Message, session: AsyncSession) -> None:
    if not await _has_factory_access(session, message.from_user.id):
        await message.answer(t("ru", "no_access"))
        return
    lang = await _lang_for(session, message.from_user.id) or "ru"

    analytics = await get_factory_analytics(session)
    if not analytics.suppliers:
        await message.answer(t(lang, "analytics_no_suppliers"))
        return

    lines = [t(lang, "analytics_header", supplier_count=analytics.supplier_count, store_count=analytics.store_count)]
    for supplier in analytics.suppliers:
        lines.append(t(lang, "analytics_supplier_line", supplier_name=supplier.supplier_name, store_count=supplier.store_count))
        for store in supplier.stores:
            lines.append(
                t(
                    lang,
                    "analytics_store_line",
                    store_name=store.store_name,
                    total_sales=store.total_sales,
                    total_points_issued=store.total_points_issued,
                )
            )
        if not supplier.stores:
            lines.append(t(lang, "analytics_store_line_empty"))

    await message.answer("\n".join(lines))


@router.message(F.text.in_(POINTS_RATE_LABELS))
async def points_rate_start(message: Message, state: FSMContext, session: AsyncSession) -> None:
    if not await _has_factory_access(session, message.from_user.id):
        await message.answer(t("ru", "no_access"))
        return
    lang = await _lang_for(session, message.from_user.id) or "ru"
    current = await customers_service.get_sum_per_point(session)
    await state.update_data(lang=lang)
    await state.set_state(PointsRateForm.waiting_value)
    await message.answer(t(lang, "points_rate_current", sum_per_point=current))


@router.message(PointsRateForm.waiting_value)
async def points_rate_save(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    lang = data["lang"]

    try:
        value = int((message.text or "").strip())
        if value <= 0:
            raise ValueError
    except ValueError:
        await message.answer(t(lang, "points_rate_invalid"))
        return

    await state.clear()
    await customers_service.set_sum_per_point(session, value)
    await message.answer(t(lang, "points_rate_saved", sum_per_point=value), reply_markup=factory_menu(lang))


async def _mint_client_file_id(source_bot: Bot, photo_file_id: str) -> str:
    """Admin uploads a photo through admin_bot, but it needs to render later in
    client_bot's catalog — Telegram file_ids are bot-scoped, so we download the bytes
    here and re-upload through a client-bot instance to a known chat (the seeded
    factory account, which has already started the client bot) to mint a file_id
    that client_bot can actually reuse."""
    buf = io.BytesIO()
    await source_bot.download(photo_file_id, destination=buf)
    buf.seek(0)

    client_bot = Bot(token=settings.bot_token)
    try:
        relay_message = await client_bot.send_photo(
            chat_id=settings.seed_factory_telegram_id,
            photo=BufferedInputFile(buf.read(), filename="product.jpg"),
        )
        return relay_message.photo[-1].file_id
    finally:
        await client_bot.session.close()


@router.message(F.text.in_(ONLINE_SHOWCASE_LABELS))
async def online_showcase(message: Message, session: AsyncSession) -> None:
    if not await _has_factory_access(session, message.from_user.id):
        await message.answer(t("ru", "no_access"))
        return
    lang = await _lang_for(session, message.from_user.id) or "ru"
    token = issue_link_token(message.from_user.id)
    link = f"{settings.miniapp_url}?token={token}"
    await message.answer(t(lang, "online_showcase_text", link=link))


@router.message(Command("set_tier"))
async def set_tier_cmd(message: Message, command: CommandObject, session: AsyncSession) -> None:
    if not await _has_factory_access(session, message.from_user.id):
        await message.answer(t("ru", "no_access"))
        return
    lang = await _lang_for(session, message.from_user.id) or "ru"

    parts = (command.args or "").split()
    if len(parts) != 2:
        await message.answer(t(lang, "set_tier_usage"))
        return
    try:
        tier, points = int(parts[0]), int(parts[1])
        if points < 0:
            raise ValueError
    except ValueError:
        await message.answer(t(lang, "set_tier_invalid"))
        return

    try:
        config = await tiers_service.set_tier_points(session, tier, points)
    except tiers_service.TierNotFoundError:
        await message.answer(t(lang, "set_tier_not_found", tier=f"{tier:,}".replace(",", " ")))
        return

    await message.answer(
        t(lang, "set_tier_saved", tier=f"{config.tier:,}".replace(",", " "), points=config.points)
    )


@router.message(Command("show_tiers"))
async def show_tiers_cmd(message: Message, session: AsyncSession) -> None:
    if not await _has_factory_access(session, message.from_user.id):
        await message.answer(t("ru", "no_access"))
        return
    lang = await _lang_for(session, message.from_user.id) or "ru"

    tiers = await tiers_service.list_tiers(session)
    if not tiers:
        await message.answer(t(lang, "show_tiers_empty"))
        return

    lines = []
    for tc in tiers:
        tier_fmt = f"{tc.tier:,}".replace(",", " ")
        status = "✅" if tc.active else "⛔️"
        lines.append(f"{status} {tier_fmt} сум → {tc.points} баллов")

    await message.answer(t(lang, "show_tiers_header") + "\n" + "\n".join(lines))


@router.message(Command("addproduct"))
async def add_product_start(message: Message, state: FSMContext, session: AsyncSession) -> None:
    if not await _has_factory_access(session, message.from_user.id):
        await message.answer(t("ru", "no_access"))
        return
    lang = await _lang_for(session, message.from_user.id) or "ru"
    await state.update_data(lang=lang)
    await state.set_state(AddProductForm.waiting_photo)
    await message.answer(t(lang, "ask_product_photo"))


@router.message(AddProductForm.waiting_photo, F.photo)
async def add_product_photo(message: Message, state: FSMContext) -> None:
    data = await state.update_data(photo_file_id=message.photo[-1].file_id)
    await state.set_state(AddProductForm.waiting_category)
    await message.answer(t(data["lang"], "ask_product_category"))


@router.message(AddProductForm.waiting_photo)
async def add_product_photo_invalid(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await message.answer(t(data["lang"], "ask_product_photo_invalid"))


@router.message(AddProductForm.waiting_category)
async def add_product_category(message: Message, state: FSMContext) -> None:
    data = await state.update_data(category=message.text)
    await state.set_state(AddProductForm.waiting_name)
    await message.answer(t(data["lang"], "ask_product_name"))


@router.message(AddProductForm.waiting_name)
async def add_product_name(message: Message, state: FSMContext) -> None:
    data = await state.update_data(name=message.text)
    await state.set_state(AddProductForm.waiting_points_cost)
    await message.answer(t(data["lang"], "ask_product_points_cost"))


@router.message(AddProductForm.waiting_points_cost)
async def add_product_points_cost(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    lang = data["lang"]

    try:
        points_cost = int((message.text or "").strip())
        if points_cost <= 0:
            raise ValueError
    except ValueError:
        await message.answer(t(lang, "points_cost_invalid"))
        return

    await state.clear()
    client_file_id = await _mint_client_file_id(message.bot, data["photo_file_id"])

    product = Product(
        name=data["name"],
        category=data["category"],
        points_cost=points_cost,
        icon_or_image_url=client_file_id,
        active=True,
    )
    session.add(product)
    await session.commit()

    await message.answer(
        t(lang, "product_created", name=data["name"], category=data["category"], points_cost=points_cost),
        reply_markup=factory_menu(lang),
    )


async def _list_for_kind(session: AsyncSession, kind: str):
    if kind == "admin":
        return await directory_service.list_admins(session)
    supplier_kind = SupplierKind.SUPPLIER if kind == "supplier" else SupplierKind.WHOLESALER
    return await directory_service.list_suppliers(session, supplier_kind)


def _entity_label(kind: str, entity) -> str:
    if kind == "admin":
        name = f"{entity.first_name or ''} {entity.last_name or ''}".strip()
        return name or f"ID {entity.telegram_id}"
    contact = f"{entity.contact_first_name or ''} {entity.contact_last_name or ''}".strip()
    return f"{contact} — {entity.name}" if contact else entity.name


async def _render_entity_list(
    message: Message, state: FSMContext, lang: str, kind: str, entities: list
) -> None:
    label_map: dict[str, int] = {}
    labels: list[str] = []
    for entity in entities:
        label = _entity_label(kind, entity)
        base_label, suffix = label, 2
        while label in label_map:
            label = f"{base_label} ({suffix})"
            suffix += 1
        entity_id = entity.telegram_id if kind == "admin" else entity.id
        label_map[label] = entity_id
        labels.append(label)

    await state.set_state(ViewUsersForm.listing)
    await state.update_data(kind=kind, entity_map=label_map)

    if not labels:
        await message.answer(t(lang, "empty_list"), reply_markup=entity_list_menu(lang, []))
        return
    await message.answer(t(lang, "entity_list_header", count=len(labels)), reply_markup=entity_list_menu(lang, labels))


async def _send_entity_detail(message: Message, session: AsyncSession, lang: str, kind: str, entity_id: int) -> None:
    if kind == "admin":
        admins = await directory_service.list_admins(session)
        entity = next((a for a in admins if a.telegram_id == entity_id), None)
        if entity is None:
            return
        name = f"{entity.first_name or ''} {entity.last_name or ''}".strip() or "—"
        await message.answer(t(lang, "admin_detail", name=name, phone=entity.phone or "—", telegram_id=entity.telegram_id))
        return

    supplier = await directory_service.get_supplier(session, entity_id)
    if supplier is None:
        return
    stores = await stores_service.list_stores_by_supplier(session, supplier.id)
    total_purchases, total_points = await get_supplier_purchase_stats(session, supplier.id)
    kind_label = t(lang, "kind_supplier" if supplier.kind == SupplierKind.SUPPLIER else "kind_wholesaler")
    await message.answer(
        t(
            lang,
            "supplier_detail",
            kind_label=kind_label,
            company_name=supplier.name,
            city=supplier.city or "—",
            first_name=supplier.contact_first_name or "—",
            last_name=supplier.contact_last_name or "—",
            phone=supplier.contact_phone or "—",
            store_count=len(stores),
            total_purchases=total_purchases,
            total_points=total_points,
        )
    )


@router.message(F.text.in_(VIEW_USERS_LABELS))
async def view_users_menu_button(message: Message, state: FSMContext, session: AsyncSession) -> None:
    await state.clear()
    if not await _has_factory_access(session, message.from_user.id):
        await message.answer(t("ru", "no_access"))
        return
    lang = await _lang_for(session, message.from_user.id) or "ru"
    await message.answer(t(lang, "choose_view_type"), reply_markup=view_users_menu(lang))


@router.message(F.text.in_(VIEW_ADMIN_LABELS))
async def view_admins(message: Message, state: FSMContext, session: AsyncSession) -> None:
    if not await _has_factory_access(session, message.from_user.id):
        await message.answer(t("ru", "no_access"))
        return
    lang = await _lang_for(session, message.from_user.id) or "ru"
    entities = await directory_service.list_admins(session)
    await _render_entity_list(message, state, lang, "admin", entities)


@router.message(F.text.in_(VIEW_SUPPLIER_LABELS))
async def view_suppliers(message: Message, state: FSMContext, session: AsyncSession) -> None:
    if not await _has_factory_access(session, message.from_user.id):
        await message.answer(t("ru", "no_access"))
        return
    lang = await _lang_for(session, message.from_user.id) or "ru"
    entities = await directory_service.list_suppliers(session, SupplierKind.SUPPLIER)
    await _render_entity_list(message, state, lang, "supplier", entities)


@router.message(F.text.in_(VIEW_WHOLESALER_LABELS))
async def view_wholesalers(message: Message, state: FSMContext, session: AsyncSession) -> None:
    if not await _has_factory_access(session, message.from_user.id):
        await message.answer(t("ru", "no_access"))
        return
    lang = await _lang_for(session, message.from_user.id) or "ru"
    entities = await directory_service.list_suppliers(session, SupplierKind.WHOLESALER)
    await _render_entity_list(message, state, lang, "wholesaler", entities)


@router.message(ViewUsersForm.listing, F.text.in_(VIEW_SEARCH_LABELS))
async def view_search_start(message: Message, state: FSMContext, session: AsyncSession) -> None:
    lang = await _lang_for(session, message.from_user.id) or "ru"
    await state.set_state(ViewUsersForm.waiting_search_phone)
    await message.answer(t(lang, "ask_search_phone"))


@router.message(ViewUsersForm.listing)
async def view_entity_clicked(message: Message, state: FSMContext, session: AsyncSession) -> None:
    lang = await _lang_for(session, message.from_user.id) or "ru"
    data = await state.get_data()
    entity_id = data.get("entity_map", {}).get(message.text)
    if entity_id is None:
        return
    await _send_entity_detail(message, session, lang, data["kind"], entity_id)


@router.message(ViewUsersForm.waiting_search_phone)
async def view_search_phone(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    kind = data.get("kind", "supplier")
    lang = await _lang_for(session, message.from_user.id) or "ru"
    query = message.text or ""

    if kind == "admin":
        results = await directory_service.search_admins_by_phone(session, query)
    else:
        supplier_kind = SupplierKind.SUPPLIER if kind == "supplier" else SupplierKind.WHOLESALER
        results = await directory_service.search_suppliers_by_phone(session, supplier_kind, query)

    if not results:
        await message.answer(t(lang, "search_not_found"))
        return
    await _render_entity_list(message, state, lang, kind, results)
