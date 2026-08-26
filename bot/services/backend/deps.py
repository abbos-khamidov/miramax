from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.db import get_session
from core.models import Role
from core.services.link_auth import InvalidLinkTokenError, verify_link_token
from core.services.telegram_auth import InvalidInitDataError, verify_init_data

get_db = get_session


@dataclass
class Principal:
    telegram_id: int
    role: str
    supplier_id: int | None
    store_id: int | None


@dataclass
class TelegramUser:
    telegram_id: int
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None


def _resolve_telegram_id(x_telegram_init_data: str | None, x_link_token: str | None) -> int:
    """The Mini App is opened either through Telegram's WebApp bridge (initData) or
    as a plain link the bot sent with a signed token embedded — either is accepted."""
    if x_telegram_init_data:
        try:
            return verify_init_data(x_telegram_init_data)["id"]
        except InvalidInitDataError as exc:
            if not x_link_token:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"invalid initData: {exc}") from exc
    if x_link_token:
        try:
            return verify_link_token(x_link_token)
        except InvalidLinkTokenError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"invalid link token: {exc}") from exc
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing credentials")


async def get_current_principal(
    x_telegram_init_data: str | None = Header(None, alias="X-Telegram-Init-Data"),
    x_link_token: str | None = Header(None, alias="X-Link-Token"),
    session: AsyncSession = Depends(get_db),
) -> Principal:
    telegram_id = _resolve_telegram_id(x_telegram_init_data, x_link_token)
    result = await session.execute(select(Role).where(Role.telegram_id == telegram_id))
    role = result.scalar_one_or_none()
    if role is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="no role assigned")

    return Principal(
        telegram_id=telegram_id,
        role=role.role.value,
        supplier_id=role.supplier_id,
        store_id=role.store_id,
    )


async def get_telegram_user(
    x_telegram_init_data: str | None = Header(None, alias="X-Telegram-Init-Data"),
    x_link_token: str | None = Header(None, alias="X-Link-Token"),
) -> TelegramUser:
    if x_telegram_init_data:
        try:
            user = verify_init_data(x_telegram_init_data)
            return TelegramUser(
                telegram_id=user["id"],
                first_name=user.get("first_name"),
                last_name=user.get("last_name"),
                username=user.get("username"),
            )
        except InvalidInitDataError as exc:
            if not x_link_token:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"invalid initData: {exc}") from exc
    if x_link_token:
        try:
            telegram_id = verify_link_token(x_link_token)
        except InvalidLinkTokenError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"invalid link token: {exc}") from exc
        return TelegramUser(telegram_id=telegram_id)
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing credentials")


def require_factory(principal: Principal = Depends(get_current_principal)) -> Principal:
    if principal.telegram_id == settings.superuser_telegram_id:
        return principal
    if principal.role not in {"factory", "admin"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="factory role required")
    return principal


def require_supplier(principal: Principal = Depends(get_current_principal)) -> Principal:
    if principal.role != "supplier":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="supplier role required")
    return principal


def require_admin(principal: Principal = Depends(get_current_principal)) -> Principal:
    if principal.telegram_id == settings.superuser_telegram_id:
        return principal
    if principal.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="admin role required")
    return principal


def require_own_supplier(supplier_id: int, principal: Principal) -> None:
    if principal.role == "factory":
        return
    if principal.role == "supplier" and principal.supplier_id == supplier_id:
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not your supplier")
