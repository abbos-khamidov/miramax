from pathlib import Path

from aiogram import F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import FSInputFile, Message
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import InviteTargetRole, RoleName
from core.services import invites as invites_service
from core.services import roles as roles_service
from services.seller_bot.handlers.seller import send_seller_menu
from services.seller_bot.handlers.supplier import send_supplier_menu
from services.seller_bot.i18n import (
    CHOOSE_LANGUAGE_FIRST_RUN,
    FIRST_RUN_INSTRUCTION,
    LANGUAGE_CODE_BY_LABEL,
    LANGUAGE_LABELS,
    t,
)
from services.seller_bot.keyboards import LANGUAGE_MENU_LABELS, language_menu

router = Router(name="supplier_seller_start")

HELP_VIDEO_PATH = Path(__file__).resolve().parents[3] / "help.mp4"


async def _send_menu(message: Message, role: RoleName, lang: str) -> None:
    if role == RoleName.SUPPLIER:
        await send_supplier_menu(message, lang)
    else:
        await send_seller_menu(message, lang)


@router.message(CommandStart(deep_link=True))
async def start_with_payload(message: Message, command: CommandObject, session: AsyncSession) -> None:
    payload = command.args or ""
    if not payload.startswith("inv_"):
        await start_cmd(message, session)
        return

    try:
        invite = await invites_service.redeem_invite(session, payload, message.from_user.id)
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

    if invite.target_role in (InviteTargetRole.SUPPLIER, InviteTargetRole.SELLER):
        await message.answer(
            "Вы зарегистрированы как поставщик Miramax Bonus."
            if invite.target_role == InviteTargetRole.SUPPLIER
            else "Вы привязаны к магазину как продавец Miramax Bonus."
        )
        await start_cmd(message, session)
        return

    await start_cmd(message, session)


@router.message(CommandStart())
async def start_cmd(message: Message, session: AsyncSession) -> None:
    role = await roles_service.get_role_by_telegram_id(session, message.from_user.id)
    if role is None or role.role not in (RoleName.SUPPLIER, RoleName.SELLER):
        await message.answer("Доступ не назначен. Обратитесь к администратору Miramax.")
        return

    if role.language is None:
        instruction_key = "supplier" if role.role == RoleName.SUPPLIER else "seller"
        await message.answer(FIRST_RUN_INSTRUCTION[instruction_key])
        await message.answer(CHOOSE_LANGUAGE_FIRST_RUN, reply_markup=language_menu())
        return

    await _send_menu(message, role.role, role.language)


@router.message(Command("help"))
async def help_cmd(message: Message, session: AsyncSession) -> None:
    role = await roles_service.get_role_by_telegram_id(session, message.from_user.id)
    if role is None or role.role not in (RoleName.SUPPLIER, RoleName.SELLER):
        await message.answer(t("ru", "no_access"))
        return
    lang = role.language or "ru"
    await message.answer(t(lang, "help_supplier" if role.role == RoleName.SUPPLIER else "help_seller"))


@router.message(F.text.in_(LANGUAGE_LABELS.values()))
async def language_chosen(message: Message, session: AsyncSession) -> None:
    role = await roles_service.get_role_by_telegram_id(session, message.from_user.id)
    if role is None or role.role not in (RoleName.SUPPLIER, RoleName.SELLER):
        await message.answer(t("ru", "no_access"))
        return
    lang = LANGUAGE_CODE_BY_LABEL[message.text]
    await roles_service.set_language(session, message.from_user.id, lang)
    await message.answer(t(lang, "language_saved"))

    if role.role == RoleName.SELLER and HELP_VIDEO_PATH.exists():
        await message.answer(t(lang, "watch_video_prompt"))
        await message.answer_video(FSInputFile(HELP_VIDEO_PATH))

    await _send_menu(message, role.role, lang)


@router.message(F.text.in_(LANGUAGE_MENU_LABELS))
async def language_menu_button(message: Message, session: AsyncSession) -> None:
    role = await roles_service.get_role_by_telegram_id(session, message.from_user.id)
    if role is None or role.role not in (RoleName.SUPPLIER, RoleName.SELLER):
        await message.answer(t("ru", "no_access"))
        return
    lang = role.language or "ru"
    await message.answer(t(lang, "choose_language"), reply_markup=language_menu())
