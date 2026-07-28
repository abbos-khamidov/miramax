"""Manual bootstrap for phase 1: no admin UI, roles are seeded directly.

Run once after migrations: `python seed.py`. Safe to re-run — skips rows that already exist.
"""
import asyncio

from sqlalchemy import select

from core.config import settings
from core.db import async_session
from core.models import Role, RoleName, Supplier


async def seed() -> None:
    async with async_session() as session:
        existing_factory = await session.execute(
            select(Role).where(Role.telegram_id == settings.seed_factory_telegram_id)
        )
        if existing_factory.scalar_one_or_none() is None:
            session.add(Role(telegram_id=settings.seed_factory_telegram_id, role=RoleName.FACTORY))
            print(f"Seeded factory role for telegram_id={settings.seed_factory_telegram_id}")
        else:
            print(f"factory role for telegram_id={settings.seed_factory_telegram_id} already exists, skipping")

        existing_supplier_role = await session.execute(
            select(Role).where(Role.telegram_id == settings.seed_supplier_telegram_id)
        )
        if existing_supplier_role.scalar_one_or_none() is None:
            supplier = Supplier(name=settings.seed_supplier_name)
            session.add(supplier)
            await session.flush()
            session.add(
                Role(
                    telegram_id=settings.seed_supplier_telegram_id,
                    role=RoleName.SUPPLIER,
                    supplier_id=supplier.id,
                )
            )
            print(
                f"Seeded supplier '{supplier.name}' (id={supplier.id}) "
                f"for telegram_id={settings.seed_supplier_telegram_id}"
            )
        else:
            print(f"supplier role for telegram_id={settings.seed_supplier_telegram_id} already exists, skipping")

        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed())
