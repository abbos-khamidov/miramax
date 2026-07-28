from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Role


async def get_role_by_telegram_id(session: AsyncSession, telegram_id: int) -> Role | None:
    result = await session.execute(select(Role).where(Role.telegram_id == telegram_id))
    return result.scalar_one_or_none()


async def set_language(session: AsyncSession, telegram_id: int, language: str) -> None:
    role = await get_role_by_telegram_id(session, telegram_id)
    if role is not None:
        role.language = language
        await session.commit()
